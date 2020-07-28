import os
import io
import uuid
import sys
import yaml
import traceback

with open('./config.yaml', 'r') as fd:
    opts = yaml.safe_load(fd)

sys.path.insert(0, './white_box_cartoonizer/')

import cv2
from flask import Flask, render_template, make_response, flash
import flask
from PIL import Image
import numpy as np

from cartoonize import WB_Cartoonize

if not opts['run_local']:
    if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
        from gcloud_utils import upload_blob, generate_signed_url, delete_blob
    else:
        raise Exception("GOOGLE_APPLICATION_CREDENTIALS not set in environment variables")
    from video_api import api_request
    # Algorithmia (GPU inference)
    import Algorithmia

app = Flask(__name__)

app.config['UPLOAD_FOLDER_VIDEOS'] = 'static/uploaded_videos'
app.config['CARTOONIZED_FOLDER'] = 'static/cartoonized_images'
app.secret_key = b'casualbakarwadi'

app.config['OPTS'] = opts

## Init Cartoonizer and load its weights 
wb_cartoonizer = WB_Cartoonize(os.path.abspath("white_box_cartoonizer/saved_models/"), opts['gpu'])

def convert_bytes_to_image(img_bytes):
    """Convert bytes to numpy array

    Args:
        img_bytes (bytes): Image bytes read from flask.

    Returns:
        [numpy array]: Image numpy array
    """
    
    pil_image = Image.open(io.BytesIO(img_bytes))
    if pil_image.mode=="RGBA":
        image = Image.new("RGB", pil_image.size, (255,255,255))
        image.paste(pil_image, mask=pil_image.split()[3])
    else:
        image = pil_image.convert('RGB')
    
    image = np.array(image)
    
    return image

@app.route('/')
@app.route('/cartoonize', methods=["POST", "GET"])
def cartoonize():
    opts = app.config['OPTS']
    if flask.request.method == 'POST':
        try:
            if flask.request.files.get('image'):
                img = flask.request.files["image"].read()
                
                ## Read Image and convert to PIL (RGB) if RGBA convert appropriately
                image = convert_bytes_to_image(img)

                img_name = str(uuid.uuid4())
                
                cartoon_image = wb_cartoonizer.infer(image)
                
                cartoonized_img_name = os.path.join(app.config['CARTOONIZED_FOLDER'], img_name + ".jpg")
                cv2.imwrite(cartoonized_img_name, cv2.cvtColor(cartoon_image, cv2.COLOR_RGB2BGR))
                
                if not opts["run_local"]:
                    # Upload to bucket
                    output_uri = upload_blob("cartoonized_images", cartoonized_img_name, img_name + ".jpg", content_type='image/jpg')

                    # Delete locally stored cartoonized image
                    os.system("rm " + cartoonized_img_name)
                    cartoonized_img_name = generate_signed_url(output_uri)
                    

                return render_template("index_cartoonized.html", cartoonized_image=cartoonized_img_name)

            if flask.request.files.get('video'):
                
                filename = str(uuid.uuid4()) + ".mp4"
                video = flask.request.files["video"]
                original_video_path = os.path.join(app.config['UPLOAD_FOLDER_VIDEOS'], filename)
                video.save(original_video_path)
                
                # Slice, Resize and Convert Video to 15fps
                modified_video_path = os.path.join(app.config['UPLOAD_FOLDER_VIDEOS'], filename.split(".")[0] + "_modified.mp4")
                width_resize=480
                os.system("ffmpeg -hide_banner -loglevel warning -ss 0 -i '{}' -t 10 -filter:v scale={}:-2 -r 15 -c:a copy '{}'".format(os.path.abspath(original_video_path), width_resize, os.path.abspath(modified_video_path)))
                
                if opts["run_local"]:
                    # if local then "output_uri" is a file path
                    output_uri = wb_cartoonizer.process_video(modified_video_path)
                else:
                    data_uri = upload_blob("processed_videos_cartoonize", modified_video_path, filename, content_type='video/mp4', algo_unique_key='cartoonizeinput')
                    response = api_request(data_uri)

                    # Delete the processed video from Cloud storage
                    delete_blob("processed_videos_cartoonize", filename)
                    output_uri = response['output_uri']
                
                # Delete the videos from local disk
                os.system("rm " + original_video_path) 
                os.system("rm " + modified_video_path)
                
                if opts["run_local"]:
                    signed_url = output_uri
                else:
                    signed_url = generate_signed_url(output_uri)

                return render_template("index_cartoonized.html", cartoonized_video=signed_url)
        
        except Exception as e:
            print(traceback.print_exc())
            flash("Our server hiccuped :/ Please upload another file! :)")
            return render_template("index_cartoonized.html")
    else:
        return render_template("index_cartoonized.html")

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
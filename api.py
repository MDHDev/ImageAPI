import flask, os
from PIL import Image, ImageDraw, ImageFont
from flask import request, send_file
from io import BytesIO

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/images/<imagename>', methods=['GET'])
def get_image(imagename):

    #Test values - leaving these incase you want to use to test. You'll need to comment out the relevant lines below.
    #img_text = "ATOM TEST"
    #img_res = 5
    #img_ext = "JPEG"
    #img_bgcolour = "BLACK"

    #Settings
    img_name = os.path.abspath(os.curdir) + '\\product_images\\' + imagename
    list_valid_extensions = ["png","jpeg","gif"]    

    #---------------------
    #Need to check that the required parameters have been supplied and are valid
    #---------------------
    #Check image exists
    if os.path.isfile(img_name):
        img = Image.open(img_name) 
    else:
        return image_not_found("Image not found")

    #Check image resolution (quality) has been supplied
    img_res = request.args.get("res", type=int)
    if not isinstance(img_res, int):
        return image_not_found("Invalid or missing resolution")

    #Check image extension has been supplied
    img_ext = request.args.get("ext", type=str)
    if not isinstance(img_ext, str) or not img_ext in list_valid_extensions:
        return image_not_found("Invalid or missing file extension")

    #---------------------
    #Set up optional parameters
    #---------------------
    img_bgcolour = request.args.get("bgcolour", type=str)
    img_text = request.args.get("text", type=str)    

    #Add watermark - if required
    if img_text is not None:
        font = ImageFont.truetype(font='arial.ttf', size=50) #Set up font
        draw = ImageDraw.Draw(im=img) #Set up draw module
        text_width, text_height = draw.textsize(text=img_text, font=font) #Find out the size of the text so it can be centred
        width, height = img.size #Image size
        x = (width - text_width)/2 #Find x centre
        y = (height - text_height)/2 #Find y centre
        draw.text(xy=(x, y), text=img_text, font=font) #Add text to image

    #Add background - if required
    if img_bgcolour is not None:
        try:
            final_img = Image.new(mode="RGB", size=img.size, color=img_bgcolour) #Create new image as background
            final_img.paste(im=img, box=(0, 0), mask=img) #Paste existing image over new image
        except:
            return image_not_found("Invalid colour")
    else:
        final_img = img.copy()
        final_img = final_img.convert(mode="RGB") #Need to copy image and convert otherwise original png was losing transparency

    #Create bytes object to allow saving to memory rather than file
    byte_io = BytesIO()
    final_img.save(fp=byte_io, format=img_ext, quality=img_res)
    byte_io.seek(0) #Return to beginning of 'file' to display image

    #Return image to browser
    return send_file(filename_or_fp=byte_io, mimetype='image/'+img_ext)    

def image_not_found(err):
    return err, 404 

app.run()

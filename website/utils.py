from flask import current_app, flash
from os import makedirs, path, remove
from uuid import uuid4
from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename

email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
phone_regex = r'^\d{10}$'

folders = {
    'ORGANIZERS_FOLDER': 'static/uploads/organizers',
    'THUMBNAILS_FOLDER': 'static/uploads/thumbnails',
    'PROOF_FOLDER': 'static/uploads/proof',
    'SUMMARY_FOLDER': 'static/uploads/summary'
}

categories = ['Classroom', 'Church', 'Cultural', 'Court', 'Community']

def create_dirs():
    for folder_name, folder_path in folders.items():
        folder = path.join(current_app.root_path, folder_path)
        makedirs(folder, exist_ok=True)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(*, image_file=None, destination=None, method='add', prev_filename=None, max_size=(120, 120)):
    if image_file is None or destination is None:
        raise ValueError("Both 'image_file' and 'destination' are required keyword arguments.")

    unique_filename = secure_filename(f"{uuid4()}.webp")

    folder = None
    for key, value in folders.items():
        if key.startswith(f'{destination.upper()}'):
            folder = value
            break

    if folder is None:
        raise ValueError(f"Folder that starts with '{destination}' not found in uploads directory.")

    webp_image = BytesIO()

    try:
        # Ensure image_file is a BytesIO object
        if isinstance(image_file, bytes):
            image_file = BytesIO(image_file)

        image = Image.open(image_file)

        # Resize the image while maintaining the aspect ratio
        if image.size[0] < max_size[0] and image.size[1] < max_size[1]:
            scale_width = max_size[0] / image.size[0]
            scale_height = max_size[1] / image.size[1]
            size = (int(scale_width * image.size[0]), int(scale_height * image.size[1]))
        else:
            size = max_size

        image = image.resize(size)

        # Save the image to the BytesIO object in WEBP format
        image.save(webp_image, format="WEBP")
        webp_image.seek(0)
    except Exception as e:
        flash(f"Error processing image: {e}", category='error')
        return None

    file_path = path.join(current_app.root_path, folder, unique_filename)

    if prev_filename is not None:
        ex_path = path.join(current_app.root_path, folder, prev_filename)

    try:
        with open(file_path, 'wb') as f:
            f.write(webp_image.getbuffer())

        # Check if the file has been saved correctly
        if not path.exists(file_path):
            flash(f"{destination.capitalize()} file not uploaded successfully.", category='error')
            return None
    except Exception as e:
        flash(f"Error saving image: {e}", category='error')
        return None

    # Handle the replace method
    if method.lower() == 'replace':
        try:
            if prev_filename:  # Check if there is a previous filename
                if path.exists(ex_path):
                    remove(ex_path)  # Attempt to delete the old file
                else:
                    flash("File to replace not found.", category='error')
        except Exception as e:
            flash(f"Error replacing file: {e}", category='error')

    return unique_filename

def delete_image(*, filename, folder):
    folder_path = None
    for key, value in folders.items():
        if key.startswith(f'{folder.upper()}'):
            folder_path = value
            break

    if folder_path is None:
        raise ValueError(f"Folder that starts with '{folder}' not found in uploads directory.")

    file_path = path.join(current_app.root_path, folder_path, filename)

    try:
        if path.exists(file_path):
            remove(file_path)
        else:
            raise FileNotFoundError(f"The file '{filename}' does not exist in folder '{folder_path}'.")
    except Exception as e:
        # Handle any unexpected errors
        flash(f"Error deleting file: {e}", category='error')

def save_pdf(pdf_file, prev_summary=None):
    if pdf_file.filename == '':
        flash('No PDF file attached.', category='error')
        return None

    if pdf_file and pdf_file.filename.endswith('.pdf'):
        filename = f'{uuid4()}.pdf'  # Generate a unique filename
        file_path = path.join(current_app.root_path, folders['SUMMARY_FOLDER'], filename)
        pdf_file.save(file_path)

        if not path.exists(file_path):
            flash('Summary PDF file not saved successfully', category='error')
            return None

        # Remove previous summary if it exists
        if prev_summary:
            prev_summary_path = path.join(current_app.root_path, folders['SUMMARY_FOLDER'], prev_summary)
            if path.exists(prev_summary_path):
                try:
                    remove(prev_summary_path)
                    flash('Previous summary removed successfully.', category='success')
                except Exception as e:
                    flash(f'Error removing previous summary: {str(e)}', category='error')

        flash('PDF summary uploaded successfully!', category='success')
        return filename

    flash('Invalid file type. Please upload a PDF file.', category='error')
    return None

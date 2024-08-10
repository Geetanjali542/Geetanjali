from django.shortcuts import render, redirect
import pandas as pd
from .models import *

import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import numpy as np

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os


# Create your views here.
def model_form_upload(request):
    if request.method == 'POST':
        description = request.POST['description'] #Retrieves the value of the form field with the name "description" from the submitted data.
        file = request.FILES['file'] #Retrieves the uploaded file from the form
        fs = Document(description=description,document=file)
        fs.save() # fs is an instance, saves this instance to the database
        file_path = fs.document.path #Gets the file path of the saved file.
        
        if file.name.endswith('.csv'):
                df = pd.read_csv(file_path)
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            print("Invalid file format")
            
        desired_columns = ['Cust State', 'Cust Pin', 'DPD'] #This specifies the columns you are interested in extracting from the file
        available_columns = [col for col in desired_columns if col in df.columns] #Checks which of the desired_columns are actually present in the uploaded file.

        df_selected = df[available_columns] #Selects the available columns from the DataFrame (df).
    
        summary = {
            'data': df_selected.head(4).to_html(index=False), #It shows the first 4 entries of the selected row from the DataFrame and to_html converts these rows to an HTML table, excluding the index column, if removes .head(4), it will show all the entries
        }


        # Create an image of the summary table
        fig, ax = plt.subplots()
        ax.axis('tight')
        ax.axis('off')
        ax.table(cellText=df_selected.head(4).values, colLabels=df_selected.columns, cellLoc='center', loc='center')

        # Save the figure as an image in memory
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

       # Save the image using Django's default storage
        image_path = f'summaries/summary_{fs.id}.png'
        image_content = ContentFile(buf.getvalue())
        fs.summary_image.save(image_path, image_content)
        fs.save()


        return render(request, 'summary.html', {
            'summary': summary
        })    
    return render(request, 'upload.html')
from celery import shared_task
import pandas as pd
from .models import Vote
from io import BytesIO
from reportlab.pdfgen import canvas
from django.conf import settings
import os
from datetime import datetime

@shared_task
def generate_report_task(from_date, to_date, export_type):
    print(">>> Running updated generate_report_task <<<")  # Debug

    from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
    to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
    votes = Vote.objects.filter(voted_at__date__gte=from_date_obj, voted_at__date__lte=to_date_obj)

    df = pd.DataFrame.from_records(votes.values('voted_at'))
    if df.empty:
        return {'status': 'no_data'}

    df['date'] = pd.to_datetime(df['voted_at']).dt.date
    report = df.groupby('date').size().reset_index(name='vote_count')

    file_name = f"vote_report_{from_date}_to_{to_date}.{export_type}"
    relative_file_path = f"reports/{file_name}"
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, 'reports', file_name)

    os.makedirs(os.path.dirname(absolute_file_path), exist_ok=True)

    if export_type == 'csv':
        report.to_csv(absolute_file_path, index=False)
    elif export_type == 'pdf':
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica", 12)
        p.drawString(50, 800, f"Vote Report from {from_date} to {to_date}")
        y = 770
        for index, row in report.iterrows():
            p.drawString(50, y, f"Date: {row['date']}, Votes: {row['vote_count']}")
            y -= 20
            if y < 50:
                p.showPage()
                y = 800
        p.save()
        buffer.seek(0)
        with open(absolute_file_path, 'wb') as f:
            f.write(buffer.read())

    
    download_url = f"/download-report/{file_name}"
    print(f"Generated download_url: {download_url}") 

    return {
        'status': 'success',
        'file_path': relative_file_path,
        'download_url': download_url
    }
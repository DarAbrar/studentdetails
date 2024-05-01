# from django.shortcuts import render
# import pandas as pd

# # Create your views here.
# def home(request):
#     if request.method == 'POST' and request.FILES['file']:
#         excel_file = request.FILES['file']
#         df = pd.read_excel(excel_file)

#         # Trim column names to remove any leading or trailing whitespace
#         df.columns = df.columns.str.strip()

#         # Specify column names after trimming whitespace
#         desired_columns = ['Mobile', 'CandidateName', 'FatherName', 'MotherName']

#         # Check if all desired columns exist in DataFrame
#         if all(column in df.columns for column in desired_columns):
#             selected_columns = df[desired_columns]

#             # Limit to the first 10 rows
#             selected_columns = selected_columns.head(10)

#             # Convert the selected columns to a dictionary
#             data_dict = selected_columns.to_dict(orient='records')

#             return render(request, 'home.html', {'data': data_dict})
#         else:
#             error_message = "One or more desired columns not found in the Excel file."
#             print(error_message)

#     return render(request, 'upload.html')



# data_import/views.py
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import ExcelUploadForm
from .models import Candidate, MarkedCandidate
import pandas as pd

def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = handle_uploaded_excel(request.FILES['file'])
            import_data(excel_data)
            return HttpResponseRedirect('/success/')
    else:
        form = ExcelUploadForm()
    return render(request, 'upload.html', {'form': form})

def handle_uploaded_excel(f):
    df = pd.read_excel(f)
    return df

def import_data(df):
    for index, row in df.iterrows():
        candidate = Candidate(
            mobile=row['Mobile'],
            candidate_name=row['CandidateName'],
            father_name=row['FatherName'],
            mother_name=row['MotherName']
        )
        candidate.save()


# views.py
from django.shortcuts import render
from .models import Candidate
import random
import json

def show_candidates(request):
    candidates = Candidate.objects.all()[:50]  # Fetch only the first 10 rows
    return render(request, 'candidates.html', {'candidates': candidates})

    candidates = [
        'Henna Kazi',
        'Andleeb Jaffar',
        'Sehran',
        'Inzimam',
        'Sameer',
        'Nadeem',
        'Sajid',
        'Imtiyaz',
        'Fiazaan',
        'Shahabbas',
        'Sharik'
    ]
    
from django.shortcuts import render
import json
import random
from .models import Candidate
# from .views import get_assigned_candidates
from django.http import JsonResponse
import json

from django.http import JsonResponse
import json
from django.template.loader import render_to_string
from django.middleware.csrf import get_token

def get_assigned_candidates(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_name = data.get('selected_name')
        if selected_name:
            # Fetch assigned candidates for the selected name
            candidates = Candidate.objects.exclude(candidate_name__in=MarkedCandidate.objects.values_list('name', flat=True))

            # Shuffle the candidates
            provided_names = [
                'Henna Kazi', 'Andleeb Jaffar', 'Sehran', 'Inzimam', 
                'Sameer', 'Nadeem', 'Sajid', 'Imtiyaz', 'Fiazaan', 
                'Shahabbas', 'Sharik'
            ]
            serialized_candidates = list(candidates)
            random.shuffle(serialized_candidates)

            # Assign candidates to names
            assigned_candidates = {}
            used_candidates = set()
            for name in provided_names:
                candidates_for_name = []
                for candidate in serialized_candidates:
                    if candidate not in used_candidates:
                        candidate_info = {
                            'name': candidate.candidate_name,
                            'mobile': candidate.mobile,
                            'father_name': candidate.father_name,
                            'mother_name': candidate.mother_name,
                            'is_marked': candidate.is_marked  # Include is_marked attribute
                            # Add more attributes as needed
                        }
                        candidates_for_name.append(candidate_info)
                        used_candidates.add(candidate)
                    if len(candidates_for_name) == 250:
                        break
                assigned_candidates[name] = candidates_for_name
            candidates_for_selected_name = assigned_candidates.get(selected_name, [])
            
            javascript_code = render_to_string('home.html', {'csrf_token': get_token(request)})
            html_response = "<table>"
            html_response += "<tr><th>Mark</th><th>Serial No.</th><th>Name</th><th>Mobile</th><th>Father's Name</th><th>Mother's Name</th></tr>"

            # Initialize a serial number counter
            serial_number = 1

            for candidate in candidates_for_selected_name:
                html_response += "<tr>"
                html_response += f'<td><input type="checkbox" onchange="toggleTextDecoration(this, \'{candidate["name"]}\')"></td>'
                html_response += f"<td>{serial_number}</td>"
                html_response += f"<td>{candidate['name']}</td>"
                html_response += f"<td>{candidate['mobile']}</td>"
                html_response += f"<td>{candidate.get('father_name', 'N/A')}</td>"
                html_response += f"<td>{candidate.get('mother_name', 'N/A')}</td>"
                html_response += "</tr>"
                
                # Increment the serial number counter
                serial_number += 1

            html_response += "</table>"
            html_response += javascript_code
            html_response += """
            <script>
                var marked_candidates = [];

                function toggleTextDecoration(checkbox, candidateName) {
                    var row = checkbox.parentNode.parentNode;
                    if (checkbox.checked) {
                        row.style.textDecoration = 'line-through';
                        marked_candidates.push(candidateName); // Add candidate to marked_candidates list

                        // Get the CSRF token from the cookie
                        var csrftoken = getCookie('csrftoken');

                        // Save the marked candidate in the database
                        $.ajax({
                            url: '/save_marked_candidate/',
                            type: 'POST',
                            headers: { 'X-CSRFToken': csrftoken },  // Include CSRF token in the headers
                            data: { 'name': candidateName },

                            success: function(data) {
                                // Handle success if needed
                            },
                            error: function(xhr, status, error) {
                                // Handle error if needed
                            }
                        });
                    } else {
                        row.style.textDecoration = 'none';
                        var index = marked_candidates.indexOf(candidateName);
                        if (index !== -1) {
                            marked_candidates.splice(index, 1); // Remove candidate from marked_candidates list
                        }
                    }
                }

                // Function to get CSRF token from cookie
                function getCookie(name) {
                    var cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                        var cookies = document.cookie.split(';');
                        for (var i = 0; i < cookies.length; i++) {
                            var cookie = cookies[i].trim();
                            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }
            </script>
            """


            candidates_for_selected_name = [candidate for candidate in candidates_for_selected_name]
            
            return JsonResponse({'html_response': html_response})
    return JsonResponse({'error': 'Invalid request'})

def save_marked_candidate(request):
    if request.method == 'POST':
        candidate_name = request.POST.get('name')
        if candidate_name:
            # Check if the candidate is already marked
            if not MarkedCandidate.objects.filter(name=candidate_name).exists():
                # If the candidate is not marked, save it in the database
                MarkedCandidate.objects.create(name=candidate_name)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Candidate already marked.'})
        else:
            return JsonResponse({'success': False, 'message': 'Name parameter missing.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def marked_candidates(request):
    # Retrieve all marked candidates
    marked_candidates = MarkedCandidate.objects.all()
    return render(request, 'marked_candidates.html', {'marked_candidates': marked_candidates})

def home(request):
    provided_names = [
        'Henna Kazi', 'Andleeb Jaffar', 'Sehran', 'Inzimam', 
        'Sameer', 'Nadeem', 'Sajid', 'Imtiyaz', 'Fiazaan', 
        'Shahabbas', 'Sharik'
    ]

    # Fetch candidates from the database
    candidates = Candidate.objects.all()

    # Shuffle the candidates
    serialized_candidates = list(candidates)
    random.shuffle(serialized_candidates)

    # Assign candidates to names
    assigned_candidates = {}
    used_candidates = set()
    for name in provided_names:
        candidates_for_name = []
        for candidate in serialized_candidates:
            if candidate not in used_candidates:
                candidates_for_name.append({
                    'name': candidate.candidate_name,
                    'mobile': candidate.mobile,
                    'father_name': candidate.father_name,
                    'mother_name': candidate.mother_name,
                })
                used_candidates.add(candidate)
            if len(candidates_for_name) == 250:
                break
        assigned_candidates[name] = candidates_for_name

    # Convert the dictionary to JSON
    assigned_candidates_json = json.dumps(assigned_candidates)

    return render(request, 'home.html', {'assigned_candidates_json': assigned_candidates_json, 'provided_names': provided_names})





# mongodb_excel/views.py
from django.http import HttpResponse
from django_pandas.io import read_frame
from pymongo import MongoClient
from io import BytesIO
import pandas as pd

def download_skillgap_excel(request):
    mongo_uri = "mongodb+srv://abrardar988651:Abrardar123@freeserver.wc1ytkf.mongodb.net/?retryWrites=true&w=majority&appName=freeServer"

    # Connect to MongoDB Atlas
    client = MongoClient(mongo_uri)
    db = client['SkillGap']
    collection = db['users']

    # Query the data
    cursor = collection.find({})  # You can add filters if needed
    print("cursor: ", cursor)
    # Convert cursor to list of dictionaries
    data = list(cursor)

    # Create DataFrame from the list of dictionaries
    df = pd.DataFrame(data)

    # Create Excel file in memory
    excel_output = BytesIO()
    df.to_excel(excel_output, index=False)
    excel_output.seek(0)

    # Set up HTTP response
    response = HttpResponse(
        excel_output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=SkillGap_data.xlsx'

    return response

def download_youthaspiration_excel(request):
    # Connect to MongoDB
    mongo_uri = "mongodb+srv://abrardar988651:Abrardar123@freeserver.wc1ytkf.mongodb.net/?retryWrites=true&w=majority&appName=freeServer"

    # Connect to MongoDB Atlas
    client = MongoClient(mongo_uri)
    db = client['YouthAspiration']
    collection = db['users']

    # Query the data
    cursor = collection.find({})  # You can add filters if needed
    print("cursor: ", cursor)
    # Convert cursor to list of dictionaries
    data = list(cursor)

    # Create DataFrame from the list of dictionaries
    df = pd.DataFrame(data)

    # Create Excel file in memory
    excel_output = BytesIO()
    df.to_excel(excel_output, index=False)
    excel_output.seek(0)

    # Set up HTTP response
    response = HttpResponse(
        excel_output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=YouthAspiration_data.xlsx'

    return response


def downloadExcel(request):
    return render(request, 'downloadexcel.html')
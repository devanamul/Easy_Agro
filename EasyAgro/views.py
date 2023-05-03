from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import project, crops, fertilizer, prePlantingProcess, postPlantingProcess, treatment
from django.core.files.storage import default_storage
from django.conf import settings 
import numpy as np
import cv2
import tensorflow as tf
import tensorflow_hub as hub
import os
from io import BytesIO
# from models import classify

def home(request):
	return render(request, "EasyAgro/home.html")

def signin(request):
	if request.method == 'GET':
		return render(request, "EasyAgro/login.html")
	elif request.method == 'POST' and 'login' in request.POST:
		u = request.POST.get('username')
		p = request.POST.get('pass')
		user = authenticate(username=u, password=p)
		if user is None:
			return render(request, "EasyAgro/login.html")
		else:
			login(request, user)
			return redirect('Dashboard')
	elif request.method == 'POST' and 'SignUp' in request.POST:
		username = request.POST.get('username')
		email = request.POST.get('email')
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		password = request.POST.get('password')
		
		
		try:
			create_user = User.objects.create_user(
				username=username,
				email=email,
				first_name=first_name,
				last_name=last_name,
				password=password
				)
		except ValueError as e:
			error_message = str(e)
			return render(request, "EasyAgro/login.html", {'error_message': error_message})
		
		create_user.save()
		messages.success(request, 'Successfully registered!')
		return redirect('SignIn')




def dashboard(request):
	u = request.user
	projects = project.objects.filter(author=u)
	return render(request, "EasyAgro/dashboard.html", {'projects': projects, 'user': u})

def projectForm(request):
	if request.method == 'GET':
		u = request.user
		return render(request, "EasyAgro/projectForm.html", {'user': u})
	elif request.method == 'POST':
		projectName = request.POST['projectName']
		landSize = request.POST['landSize']
		cropType = request.POST['CropType']
		u = request.user

		print(cropType)

		crop = crops.objects.get(name = cropType)

		newProject = project(author = u, crop = crop, name = projectName, area = landSize, status = 'Running')
		newProject.save()
		return redirect('Dashboard')

def Project(request):
	if request.method == 'GET':
		u = request.user
		project_id = request.GET.get('project_id')
		c_project = project.objects.get(id=project_id)
		return render(request, "EasyAgro/project.html", {'project': c_project, 'user': u})
	
def diseaseIdentification(request):
	if request.method == 'GET':
		return render(request, "EasyAgro/disease.html")

	elif request.method == 'POST':
		os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
		model_path = os.path.join(os.path.dirname(__file__), 'models', 'my_model.h5')
		model = tf.keras.models.load_model(model_path, custom_objects={'KerasLayer':hub.KerasLayer})

		uploaded_image = request.FILES['img']
		image_bytes = uploaded_image.read()

		image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
		print(image.shape)
		image = cv2.resize(image, (224, 224))
		image = np.array(image) / 255.0
		image = np.expand_dims(image, axis=0)

		prediction = model.predict(image)

		predicted_label = np.argmax(prediction)

		labels = {}
		labels[0] = "Early Blight"
		labels[1] = "Healthy"
		labels[2] = "Late Blight"

		result = labels[predicted_label]

		if result == "Healthy":
			pesticides = "দরকার নেই"
			advice = "ভালো ফলন পেতে নিয়মিত সার প্রয়োগ করুন"
		else:
			trmnt = treatment.objects.get(diseaseName=result)
			advice = trmnt.advice
			pesticides = trmnt.pesticides

		context = {
			'result': result,
			'advice': advice,
			'pesticides': pesticides
		}

		return render(request, "EasyAgro/disease.html", context)

def Fertilizer(request):
	if request.method == 'GET':
		u = request.user
		project_id = request.GET.get('project_id')
		print("id: ", project_id)
		c_project = project.objects.get(id=project_id)
		print("Neme ", c_project.name)
		crop = c_project.crop
		Area = c_project.area
		print(Area)
		F = fertilizer.objects.get(crop=crop)
		N = F.nitrogen
		P = F.phosphorous
		K = F.potassium

		needed_N = round((N*Area),2)
		needed_P = round((P*Area),2)
		needed_K = round((K*Area),2) 

		# print(needed_N, needed_P, needed_K)
		# print(N, P, K)
		context = {

		  'project' : c_project,
		  'needed_N': needed_N,
		  'needed_P': needed_P,
		  'needed_K': needed_K,
		  'user': u
		}
		return render(request, "EasyAgro/fertilizer.html", context)

def prePlanting(request):
	if request.method == 'GET':
		u = request.user
		project_id = request.GET.get('project_id')
		print("id: ", project_id)
		c_project = project.objects.get(id=project_id)
		print("Neme ", c_project.name)
		crop = c_project.crop
		process = prePlantingProcess.objects.get(crop=crop)

		depth = process.depth
		spacing = process.spacing
		irrigation = process.irrigation
		drainage = process.drainage
		time = process.drainage

		print("ccc ",depth, spacing, irrigation, drainage, time)

		context = {
			'project': c_project,
			'depth': depth,
			'spacing': spacing,
			'irrigation': irrigation,
			'drainage': drainage,
			'time': time,
			'user': u
		}

		return render(request, "EasyAgro/prePlanting.html", context)

def postPlanting(request):
	if request.method == 'GET':
		u = request.user
		project_id = request.GET.get('project_id')
		print("id: ", project_id)
		c_project = project.objects.get(id=project_id)
		print("Neme ", c_project.name)
		crop = c_project.crop
		process = postPlantingProcess.objects.get(crop=crop)

		depth = process.depth
		spacing = process.spacing
		irrigation = process.irrigation
		drainage = process.drainage
		time = process.time

		print("ccc ",depth, spacing, irrigation, drainage, time)

		context = {
			'project': c_project,
			'depth': depth,
			'spacing': spacing,
			'irrigation': irrigation,
			'drainage': drainage,
			'time': time,
			'user': u
		}
		return render(request, "EasyAgro/postPlanting.html", context)

def signout(request):
	logout(request)
	return redirect('homepage')
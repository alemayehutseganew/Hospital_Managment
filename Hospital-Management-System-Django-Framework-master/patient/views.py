from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate,login ,logout ,get_user_model
from django.contrib.auth.decorators import login_required
from userSystem.models import User,CustomUser
from hospital.models import Patient
from hospital.models import *
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
import json
import datetime
from django.contrib import messages
from userSystem.forms import CustomUserProfileForm
from .models import*
# Create your views here.

User = get_user_model()


# @login_required(login_url='UserLogin')
def homePatient(request):
        userid=request.user.id
        # patient = Patient.objects.get(userID=userid)
        #profile pic
        try:
        # Check if a patient record exists for the current user
            patient = Patient.objects.get(userID=userid)
        except Patient.DoesNotExist:
        # If not, create a new patient record for the user
            patient = Patient.objects.create(userID=request.user, patient_uhid=generate_uhid())  # Assume you have a method to generate a uhid
    

        formset = CustomUserProfileForm()
        context={'patient':patient,'formset':formset,}
       
        return render(request, "patientApp/home.html",context)

#New Appointmetnt Patient
#Redirect unauthorized user's from accessing home page
# @login_required(login_url='UserLogin')
# @never_cache
# def patientNewbooking(request):
#     userid=request.user.id
#     #getting basic patient details
#     patient = Patient.objects.get(userID_id=userid)
    

#     #hospital = serializers.serialize("json", Hospital.objects.all())
#     #gethospital
#     hospital =   json.dumps( list(Hospital.objects.values('name','district','hos_type','id')) ) 

#     context={'patient':patient , 'hospital':hospital, }
#     return render(request, 'patientApp/newBooking.html',context)



@login_required(login_url='UserLogin')
@never_cache
def patientNewbooking(request):
    userid = request.user.id
    
    try:
        # Check if a patient record exists for the current user
        patient = Patient.objects.get(userID=userid)
    except Patient.DoesNotExist:
        # If not, create a new patient record for the user
        patient = Patient.objects.create(userID=request.user, patient_uhid=generate_uhid())  # Assume you have a method to generate a uhid
    
    # Getting hospital data
    hospital = json.dumps(list(Hospital.objects.values('name', 'district', 'hos_type', 'id')))

    context = {'patient': patient, 'hospital': hospital}
    return render(request, 'patientApp/newBooking.html', context)

# Example function to generate a unique patient UHID
def generate_uhid():
    import random
    return random.randint(1000000000, 9999999999)  # Generating a 10-digit number


#choose doctor for Patient
#Redirect unauthorized user's from accessing home page
@login_required(login_url='UserLogin')
@never_cache
def patientChooseDoctor(request):

    userid=request.user.id
    #getting basic patient details
    patient = Patient.objects.get(userID_id=userid)

    if request.method == 'POST':


        #getting form submitted values
        selectedHosDistrict = request.POST['hospital_district']
        selectedHosType = request.POST['hospital_type']
        selectedHosName = request.POST['hospital_name']
        selectedHosDepartment = request.POST['hospital_department']

        #get hospital id
        hospitalId =  Hospital.objects.values_list('id', flat=True).get(name=selectedHosName)
       
        #get doctor and time slot of doctor
        doctorDetailsID = List.objects.filter(hospital_id=hospitalId).values('doctor_id','timeslot_id','department_id') 

        doctorDetails=[]
        for i in doctorDetailsID:
            #doctor user id
            doctorUserId=Doctor.objects.values_list('userID_id', flat=True).get(id=i['doctor_id']) 
            #getting doctor name and timeslot
            doc ={
            'doctorID':i['doctor_id'],
            'doctorName':CustomUser.objects.values_list('first_name', flat=True).get(id=doctorUserId), 
            'doctorSlot':Timing.objects.values_list('timeslot', flat=True).get(id=i['timeslot_id']),
            'doctorDep':Department.objects.values_list('name', flat=True).get(id=i['department_id'])}

            doctorDetails.append(doc)
       
        context={
            'patient':patient, 
            'selectedHosDistrict':selectedHosDistrict , 
            'selectedHosType':selectedHosType, 
            'selectedHosName':selectedHosName,
            'selectedHosDepartment':selectedHosDepartment,
            'doctorDetails':json.dumps(doctorDetails)}
        return render(request, 'patientApp\chooseDoctor.html',context)

#choose doctor for Patient
#Redirect unauthorized user's from accessing home page
def patientSaveBooking(request,dep ,hosname ,uhid):

    if request.method == 'POST':


        #getting data
        selectedDoctor = request.POST['doctor_name']
        selectedTimeslot = request.POST['doctor_timeSlot']
        selectedAppointDate = request.POST['AppointDate']
        selectedHospital = hosname

        #getting all ids
        # docId=Doctor.objects.values_list('id', flat=True).get(name=selectedDoctor)
        docId=selectedDoctor
        depId=Department.objects.values_list('id', flat=True).get(name=dep)
        timeSlotId=Timing.objects.values_list('id', flat=True).get(timeslot=selectedTimeslot)
        hosId=Hospital.objects.values_list('id', flat=True).get(name=hosname)

        #getting id of list
        listsid=List.objects.values_list('id', flat=True).get(department_id=depId,doctor_id=docId,hospital_id=hosId,timeslot_id=timeSlotId)
        patientid=Patient.objects.values_list('id', flat=True).get(patient_uhid=uhid)

        userid=request.user.id
        #getting basic patient details
        patient = Patient.objects.get(userID_id=userid)
        context={
                'patient':patient}


        if(BookingPatient.objects.filter(appointmentDate=selectedAppointDate,patient_id=patientid,lists_id=listsid).exists()):

            messages.error(request, 'You have already booked with same details , please check the My booking page')   
            return render(request, 'patientApp/BookingSucess.html',context)



        else:

            bookingpatient=BookingPatient.objects.create(state='PENDING',patient_id=patientid,lists_id=listsid ,appointmentDate=selectedAppointDate )
            bookingpatient.save()

           
            messages.success(request, 'Your boooking successfully completed')  
            return render(request, 'patientApp/BookingSucess.html',context)

#get Deparment
def getHospitalDepartment(request):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
      if request.method == 'POST':
        #loading all data
        getdata=json.load(request) 
        #getting hospital id
        gethospital_id = getdata['hospital_id']
        #geting all ids from list 
        getdepartment_ids =  List.objects.filter(hospital_id=gethospital_id).values('department_id')
        
        getdepartmentValue=[]

        #appending values from department table

        for i in getdepartment_ids:
            getdepartmentValue.append( list(Department.objects.filter(id=i['department_id']).values('name')) )
       
     
    
        data={
            'getdepartmentValue':getdepartmentValue
        }
     
        return JsonResponse(data)
    else:
        return redirect('patient-home')


#Patient Profile Booking
#Redirect unauthorized user's from accessing home page
@login_required(login_url='UserLogin')
def patientViewBooking(request):

    userid=request.user.id
    #getting basic patient details
    patient = Patient.objects.get(userID_id=userid)

    #getting patient ID
    patientId = Patient.objects.values_list('id', flat=True).get(userID_id=userid)

    #getting booking list of that patient
    bookingList = list(BookingPatient.objects.filter(patient_id=patientId).values('id','lists_id','state','appointmentDate','documents').order_by('appointmentDate') )
    #getting all ids
    eachListID=[]
    for i in bookingList:
            eachListIDs ={'doctor_id':List.objects.values_list('doctor_id', flat=True).get(id=i['lists_id']),
                        'timeslot_id':List.objects.values_list('timeslot_id', flat=True).get(id=i['lists_id']),
                        'department_id':List.objects.values_list('department_id', flat=True).get(id=i['lists_id']),
                        'hospital_id':List.objects.values_list('hospital_id', flat=True).get(id=i['lists_id']),
                        'state':i['state'],
                        'documents':i['documents'],
                        'appointmentDate':str(i['appointmentDate']),
                        'bkTableToken':i['id'],
                         }
            eachListID.append(eachListIDs)   
    
    finalBookingList=[]
    #getting all values
    for j in eachListID:
            #userid of doctor
            doctorUserId=Doctor.objects.values_list('userID_id', flat=True).get(id=j['doctor_id'])  
          
           
             #getting doctor name and timeslot
            eachListName ={ 'doctorName':CustomUser.objects.values_list('first_name', flat=True).get(id=doctorUserId), 
                        'doctorSlot':Timing.objects.values_list('timeslot', flat=True).get(id=j['timeslot_id']),
                        'doctorDep':Department.objects.values_list('name', flat=True).get(id=j['department_id']),
                        'hospital':Hospital.objects.values_list('name', flat=True).get(id=j['hospital_id']),
                        'state':j['state'],
                        'documents':j['documents'],
                        'appointmentDate':str(j['appointmentDate']),
                        'bkTableToken':j['bkTableToken'],
                        }
            finalBookingList.append(eachListName)
    context={
            'patient':patient,'bookinglist':finalBookingList}

    return render(request, 'patientApp/ViewBooking.html',context)

#Patient Profile 
#Redirect unauthorized user's from accessing 
@login_required(login_url='UserLogin')
def patientMyProfile(request):

    userid=request.user.id
    #getting basic patient details
    patient = Patient.objects.get(userID_id=userid)
    #profile pic
    formset = CustomUserProfileForm()
    context={'patient':patient,'formset':formset,}

    return render(request, 'patientApp/myprofile.html',context)



#mark deleted for booking
@login_required(login_url='UserLogin')
def patientMarkDeleted(request,id ):
       change = BookingPatient.objects.get(id=id)
       change.state = "DELETED"   # change field
       change.save() # this will update only
       change.documents.delete()

       return redirect("patientViewBooking")


#user pro pic
def uploadPatientPropic(request,id):
        if request.method == "POST":
            a = CustomUser.objects.get(pk=id)
            form = CustomUserProfileForm(request.POST, request.FILES,instance=a)
            if form.is_valid(): 
                form.save()
            return redirect("patientMyProfile")
        


#viewboooking bcp


# #Patient Profile Booking
# #Redirect unauthorized user's from accessing home page
# @login_required(login_url='login')
# def patientViewBooking(request):

#     userid=request.user.id
#     #getting basic patient details
#     patient = Patient.objects.get(userID_id=userid)

#     #getting patient ID
#     patientId = Patient.objects.values_list('id', flat=True).get(userID_id=userid)

#     #getting booking list of that patient
#     bookingList = list(BookingPatient.objects.filter(patient_id=patientId).values('lists_id','state','appointmentDate').order_by('appointmentDate') )
#     #getting all ids
#     eachListID=[]
#     for i in bookingList:
#             eachListIDs ={'doctor_id':List.objects.values_list('doctor_id', flat=True).get(id=i['lists_id']),
#                         'timeslot_id':List.objects.values_list('timeslot_id', flat=True).get(id=i['lists_id']),
#                         'department_id':List.objects.values_list('department_id', flat=True).get(id=i['lists_id']),
#                         'hospital_id':List.objects.values_list('hospital_id', flat=True).get(id=i['lists_id']),
#                         'state':i['state'],
#                         'appointmentDate':str(i['appointmentDate'])
#                          }
#             eachListID.append(eachListIDs)   
   
#     finalBookingList=[]
#     #getting all values
#     for j in eachListID:
#             #userid of doctor
#             doctorUserId=Doctor.objects.values_list('userID_id', flat=True).get(id=j['doctor_id'])  
          
           
#              #getting doctor name and timeslot
#             eachListName ={ 'doctorName':CustomUser.objects.values_list('first_name', flat=True).get(id=doctorUserId), 
#                         'doctorSlot':Timing.objects.values_list('timeslot', flat=True).get(id=j['timeslot_id']),
#                         'doctorDep':Department.objects.values_list('name', flat=True).get(id=j['department_id']),
#                         'hospital':Hospital.objects.values_list('name', flat=True).get(id=j['hospital_id']),
#                         'state':j['state'],
#                         'appointmentDate':str(j['appointmentDate'])
#                         }
#             finalBookingList.append(eachListName)

#     context={
#             'patient':patient,'bookinglist':json.dumps(finalBookingList)}

#     return render(request, 'patientApp/ViewBooking.html',context)
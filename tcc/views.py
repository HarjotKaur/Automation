"""
%% views.py %%

This file is used to create the views for the software. 
It is the interface between the user interface, urls and database.
"""

#::::::::::::::IMPORT THE HEADER FILE HERE::::::::::::::::::::#
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Max ,Q, Sum
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sessions.models import Session
from django.shortcuts import render
from django.db.models import F
from django import template
from tagging.models import Tag, TaggedItem
from Automation.tcc.choices import *
from Automation.tcc.models import *
from Automation.tcc.functions import *
from Automation.tcc.forms import *
from Automation.tcc.convert_function import *
from django.core.mail import send_mail
import fuzzy
from django.db.models.sql import constants
from django.db.models.fields import __init__
from django.db.backends.mysql import base
#import Automation.tcc.soundex import *
#from spec.soundex import soundex
#from django import soundex
#from ajax_search.forms import SearchForm
          
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#

#:::::::::::::::DEFINE THE FUNCTIONS HERE:::::::::::::::::::::#

def material_site():
	"""
	This function is to be used through out the functions in the file. 
	The	objects defined ere like the college name and the software 
	name is to be used by nearly all the templates of the software.
	"""
	material = Material.objects.all().filter(report=1)
	field = Material.objects.all().filter(report=2)
	title = Department.objects.get(id=1)	
	address = get_object_or_404(Organisation, pk='1')
	report = Report.objects.all()
	work = Govt.objects.all()
	payment = Payment.objects.all()
	template = {'material':material, 'field':field, 'title':title, 
	'address':address, 'report':report, 'work':work, 'payment':payment}
	return template

tmp = material_site()

job = Job.objects.aggregate(Max('id'))
jobmaxid = job['id__max']

def index1(request):
	'''
	** index1 **

	This is to have different views for different type of users. Like 
	here we have 2 types of users :one which is active,staff and is 
	superuser is the superuser of the software. The one who is just 
	active is the normal user. Depending upon there status different 
	views are created in index1.html and index2.html respectively. 
	'''
	id = Job.objects.aggregate(Max('job_no'))
	maxid = id['job_no__max']
	if maxid == None :
		maxid = 1
	else:
		maxid = maxid + 1
	template = {'maxid':maxid,}
	if request.user.is_staff == 1 and request.user.is_active == 1 and \
	request.user.is_superuser == 1:
		return render_to_response('index1.html',dict(template.items() + 
		tmp.items()),context_instance=RequestContext(request))
	elif request.user.is_staff == 0 and request.user.is_active == 1 \
	and request.user.is_superuser == 0 :
		try:
   			use = request.user
			client = UserProfile.objects.get(user_id = use)
			clients = client.id
			template ={'clients':clients,'maxid':maxid,}
			return render_to_response('index2.html',dict(template.items() 
			+ tmp.items()), context_instance=RequestContext(request))
		except UserProfile.DoesNotExist:
   			return render_to_response('index2.html',dict(template.items()  
   			+ tmp.items()), context_instance=RequestContext(request))
	else:
		return render_to_response('index.html', tmp ,context_instance = 
		RequestContext(request))

@login_required
def edit_profile(request):
	"""
	** edit_profile **
	
	This function firstly checks whether the user has already got a
	profile or not. If it already has, then he is offered an already
	built profile to edit, however in other case when the profile is
	not built, user is allowed to fill an empty userprofile form.
	"""
	user = User.objects.get(id=request.GET['id'])
	try :
		maxid = UserProfile.objects.get(user_id=user)
		if request.method == "POST":
			form = UserProfileForm(request.POST,instance=maxid)
			if form.is_valid():
				pro = form.save(commit=False)
				pro.user = request.user
				pro.save()
				form.save()	
				x = {'form': form, 'maxid':maxid}
				return render_to_response('tcc/new_client_ok.html', 
				dict(x.items() + tmp.items()), context_instance=
				RequestContext(request))
		else:	
			form = UserProfileForm(instance=maxid)
		x = {'form': form,}
		return render_to_response('tcc/client.html',dict(x.items() + 
		tmp.items()), context_instance = RequestContext(request))
	except:
		if request.method == "POST":
			form = UserProfileForm(request.POST)
			if form.is_valid():
				pro = form.save(commit=False)
				pro.user = request.user
				pro.save()
				form.save()	
				x = {'form': form,}
				return render_to_response('tcc/new_client_ok.html', 
				dict(x.items() + tmp.items()), context_instance=
				RequestContext(request))
		else:	
			form = UserProfileForm()
		x = {'form': form,}
		return render_to_response('tcc/client.html',dict(x.items() + 
		tmp.items()), context_instance = RequestContext(request))
	

   			
@login_required
def profile(request):
	"""
	** profile **

	This function is used to make the user fill the personal detail. 
	If a normal user fills the detail, then his userprofile get updated, 
	but if a superuser creates a profile that means he/she is 
	registering the client and registration of client can be done as m
	any times as possible.
	"""
	if request.method == 'POST':
		form = UserProfileForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			user = request.user
			first_name = cd['first_name']
			middle_name = cd['middle_name']
			last_name = cd['last_name']
			company = cd['company']
			address = cd['address']
			city = cd['city']
			pin_code = cd['pin_code']
			state = cd['state']
			website = cd['website']
			contact_no = cd['contact_no']
			type_of_organisation = cd['type_of_organisation']
			'''pro = form.save(commit=False)
			pro.user = request.user
			pro.save()
			form.save()'''
			pro = UserProfile(first_name = first_name, middle_name =
			middle_name, last_name = last_name, company = company, 
			address = address, city = city, pin_code = pin_code, state 
			= state, website = website, contact_no = contact_no, 
			type_of_organisation = 
	type_of_organisation, user = user)
			pro.save()
			id = UserProfile.objects.aggregate(Max('id'))
			maxid =id['id__max']	
			x = {'form': form,'maxid':maxid,}	
			return render_to_response('tcc/new_client_ok.html',dict(x\
			.items() + tmp.items()), context_instance=RequestContext(\
			request))
	else:
		form = UserProfileForm()
	form = {'form':form}
	if request.user.is_staff == 1 and request.user.is_active == 1 and \
	request.user.is_superuser == 1:
		return render_to_response('tcc/new_client.html',dict(form.items() + 
		tmp.items()),context_instance=RequestContext(request))
	else :
		return render_to_response('tcc/client/addprofile.html', dict(\
		form.items()+ tmp.items()), context_instance=
		RequestContext(request))

@login_required
def non_payment_job(request):
	"""
	** non_payment_job **

	This function displays the form to fill the non payment job, that
	means the job that describes the work to be done without making
	any payment.
	"""
	id = NonPaymentJob.objects.aggregate(Max('job_no'))
	maxid =id['job_no__max']
	if maxid== None :
		maxid = 1
	else:
		maxid = maxid + 1
	user = UserProfile.objects.get(id=request.GET['id'])
	if request.method == 'POST':
		form = NonPaymentJobForm(request.POST)
		if form.is_valid():
			profile = form.save(commit=False)
			profile.client= user
			profile.job_no = maxid
			profile.save()
			form.save_m2m()
			x = {'form': form,}		
			return render_to_response('tcc/nonpayment_job_ok.html',
			dict(x.items() + tmp.items()), context_instance=
			RequestContext(request))
	else:
		form = NonPaymentJobForm()
	form = {'form':form, 'maxid':maxid}
	return render_to_response('tcc/non_payment_job.html',dict(form.\
	items() + tmp.items()),context_instance=RequestContext(request))
	

@login_required
def performa(request):
	"""
	** performa **

	Gives the detailed view of profile filled by client. Just the data 
	is extracted from UserProfile table.
	"""

	user = User.objects.get(id=request.GET['id'])
	try :
		perf = UserProfile.objects.filter(user_id=user)
		temp = {'perf' : perf, 'user':user,}
		return render_to_response('tcc/client/detail.html',dict(temp.\
		items() +tmp.items()), context_instance=RequestContext(request))
	except:
		return render_to_response("tcc/profile_first.html", tmp, 
		context_instance=RequestContext(request) )

@login_required
def previous(request):
	"""
	** previous **

	This function lists the previous jobs of the user who have logged 
	in the software. Just filters the jobs done by user from the Job 
	table.
	"""
	user = User.objects.get(id=request.GET['id'])
	try :
		previous = UserProfile.objects.get(user_id=user)
		job = Job.objects.all().filter(client_id = previous)
		temp = {'job':job,}
		return render_to_response('tcc/previous.html', dict(temp.items() + 
		tmp.items()), context_instance=RequestContext(request))
	except:
		return render_to_response("tcc/profile_first.html", tmp, 
		context_instance=RequestContext(request))

'''
@login_required
def advanced_payment(request):
	try : 
		client =UserProfile.objects.get(id=request.GET['id'])
		add = Clientadd.objects.aggregate(Max('id'))   
		addid =add['id__max']
		if addid == client:
			pass
		else:
			user = request.user
			m = Clientadd(client = client,user=user)
			m.save()
		
		return render_to_response('tcc/typeofwork.html', 
		dict(temp.items() + tmp.items()), context_instance=RequestContext(request))
	except Exception:
		return render_to_response('tcc/profile_first.html',tmp, context_instance 
		= RequestContext(request))'''

def material(request):
	"""
	** material **

	Material Function lists all the materials or field works. These are the 
	links, depending on the selection of material selected, there tests are 
	filtered.
	"""
	material = Material.objects.all().order_by('name')
	return render_to_response('tcc/field.html', tmp, context_instance = 
	RequestContext(request))

def rate(request):
	"""
	** rate **

	Rate Function gets the value of material(that was selected 
	previously) from the url and based on that material, the tests 
	are listed.
	"""
	
	lab = Lab.objects.all().order_by('code')
	mat = Material.objects.get(id=request.GET['id'])
	test = Test.objects.filter(material_id = mat)
	temp = {'lab':lab,'test':test,'mat':mat,}
	return render_to_response('tcc/test.html', dict(temp.items() + 
	tmp.items()),context_instance=RequestContext(request))
	

@login_required
def selectfield(request):
	"""
	** selectfield **

	List the type of work to be done i.e Lab or Field work. It also
	checks the url, if the url shows jobno as empty, then job_no is
	incremented in clientadd table else it is assubed that new work is
	added to same job_no and thus the job_no in clientadd remains
	same.
	"""
	try : 
		client =UserProfile.objects.get(id=request.GET['id'])
		user = request.user
		jobno = request.GET.get('job','')
		if jobno =='':
			id = Clientadd.objects.aggregate(Max('job_no'))
			maxid =id['job_no__max']
			if maxid== None :
				maxid = 1
			else:
				maxid = maxid + 1
		else:
			maxid = jobno
		m = Clientadd(client = client,user=user,job_no=maxid)
		m.save()
		client = Clientadd.objects.aggregate(Max('id'))
		client =client['id__max']
		report = Report.objects.all()
		mat = Material.objects.all()
		temp = {'report':report,'mat':mat,'client':client}
		return render_to_response('tcc/typeofwork.html', 
		dict(temp.items() + tmp.items()), context_instance=
		RequestContext(request))
	except Exception:
		return render_to_response('tcc/profile_first.html',tmp, 
		context_instance = RequestContext(request))

@login_required
def select(request):
	"""
	** select **

	List down the materials or the field work depending on the 
	selection of the type of work i.e lab or Field work. However is
	the report_type is 3 or 4 means, the work to be done is CDF or
	advances payment, then the form for the same is opened to be
	filled.
	"""	
	
	mat = Material.objects.all()
	material = Report.objects.get(id=request.GET['id'])
	client = Clientadd.objects.get(id=request.GET['client'])
	clid = client.id
	report = material.id
	if report == 3 or report == 4:
		if request.method=='POST':
			form1 = AdvancedForm(request.POST)
			form2 = BillForm(request.POST)
			if form1.is_valid and form2.is_valid():
				def clean_name(self):
					cleaned_data = self.cleaned_data
					net_total = cleaned_data.get('net_total', '')
					balance = cleaned_data.get('net_total', '')
				profile = form1.save(commit=False)
				id = Bill.objects.aggregate(Max('job_no'))
				maxid =id['job_no__max']
				if maxid== None :
					maxid = 1
				else:
					maxid = maxid + 1
				profile.job_no = maxid
				profile.ip = request.META.get('REMOTE_ADDR')
				profile.client = client
				profile.report_type = material
				profile.save()
				form1.save_m2m()
				profile1 = form2.save(commit=False)		
				profile1.job_no = maxid
				
				profile1.save()
				form2.save_m2m()
				id = Bill.objects.aggregate(Max('id'))
				maxid =id['id__max']
				bill = Bill.objects.get(id=maxid)
				bal = bill.net_total
				Bill.objects.filter(id = maxid).update( balance = 
				bill.net_total)
				temp = {'maxid':maxid}
				return render_to_response('tcc/advanced_ok.html', 
				dict(temp.items() + tmp.items()), context_instance=
				RequestContext(request))
		else:	
			form1 = AdvancedForm()
			form2 = BillForm()
		return render_to_response('tcc/advanced_job.html', tmp,
		context_instance=RequestContext(request))
	else :
		field_list = Material.objects.all().filter(report_id =material)
		temp = {'field_list':field_list,'mat':mat,'clid':clid}
		return render_to_response('tcc/tags.html',dict(temp.items() + 
		tmp.items()),context_instance = RequestContext(request))

@login_required
def add_job(request):
	"""
	** add_job **

	This helps the user to add the job. Depending upon the material 
	selected the tests are listed then. Two forms are defined in a 
	single template file, so that there data get stored in different 
	tables one after the other. One is clientJob and other is
	SuspenceJob.
	"""
	query =request.GET.get('q', '')
	client = Clientadd.objects.get(id=request.GET['client'])
	clid = client.id
	maxid = client.job_no
	material =Material.objects.get(id=request.GET['q'])
	test = Test.objects.all().filter(material_id = query)
	if material.report.name == "LAB":
		field_list = Material.objects.all().filter(report_id = 1)
		if request.method=='POST':
			form1 = JobForm(request.POST)
			form2 = ClientJobForm(request.POST)
			if form1.is_valid and form2.is_valid():
				def clean_name(self):
					cleaned_data = self.cleaned_data
					pay = cleaned_data.get('pay', '')
					check_number = cleaned_data.get('check_number', '')
					check_dd_date = cleaned_data.get('check_dd_date', '')
					sample = cleaned_data.get('sample', '')
					letter_no = cleaned_data.get('letter_no','')
				profile = form1.save(commit=False)
				profile.job_no = maxid
				profile.ip = request.META.get('REMOTE_ADDR')
				profile.client = client
				report = Report.objects.get(id=1)
				profile.report_type = report
				profile.save()
				form1.save_m2m()
				test = request.POST.getlist('test')
				profile1 = form2.save(commit=False)		
				profile1.material = material
				jbmx = Job.objects.aggregate(Max('id'))
				jobmax =jbmx['id__max']
				job = Job.objects.get(id =jobmax)
				profile1.job = job
				profile1.save()
				form2.save_m2m()
				if profile.report_type == "2":
					return HttpResponseRedirect(reverse('Automation.tcc.views.add_suspence'))
				else :
					return HttpResponseRedirect(reverse('Automation.tcc.views.gen_report'))
		else:	
			form1 = JobForm()
			form2 = ClientJobForm()
		temp = {"form1": 
		form1,"test":test,'field_list':field_list,'query':query,'clid'
		:clid}
		return render_to_response('tcc/add_job.html', dict(temp.items() + 
		tmp.items()), context_instance=RequestContext(request))
	else :
		field_list = Material.objects.all().filter(report_id = 2)
		if request.method=='POST':
			form1 = JobForm(request.POST)
			form2 = SuspenceJobForm(request.POST)
  			if form1.is_valid and form2.is_valid():
				def clean_name(self):
					cleaned_data = self.cleaned_data
					pay = cleaned_data.get('pay', '')
					check_number = cleaned_data.get('check_number', '')
					check_dd_date = cleaned_data.get('check_dd_date', '')
					sample = cleaned_data.get('sample', '')
					letter_no = cleaned_data.get('letter_no','')
				profile = form1.save(commit=False)
				profile.job_no = maxid
				profile.ip = request.META.get('REMOTE_ADDR')
				profile.client = client
				report = Report.objects.get(id=2)
				profile.report_type = report
				profile.save()
				form1.save_m2m()
				profile1 = form2.save(commit=False)	
				profile1.job_no = maxid	
				profile1.field = material
				jbmx = Job.objects.aggregate(Max('id'))
				jobmax =jbmx['id__max']
				client = Job.objects.get(id =jobmax)
				profile1.job = client
				sel_test = get_object_or_404(Test, pk=request.POST.\
				get('test'))
				profile1.test = sel_test
				profile1.save()
				form2.save_m2m()
				return HttpResponseRedirect(reverse('Automation.tcc.views.add_suspence'))
		else:	
			form1 = JobForm()
			form2 = SuspenceJobForm()
			temp ={"form1": form1,"test":test,'field_list':field_list,
			'query':query}
			return render_to_response('tcc/add_suspence.html',
			dict(temp.items() + tmp.items()) , context_instance=
			RequestContext(request))
	
@login_required
def add_job_other_test(request):
	"""
	** add_job_other_test **

	This helps the user to add the job. Depending upon the material 
	selected the tests are listed then. Two forms are defined in a 
	single template file, so that there data get stored in different 
	tables one after the other.
	"""
	query =request.GET.get('q', '')
	id = Bill.objects.aggregate(Max('job_no'))
	maxid =id['job_no__max']
	if maxid== None :
		maxid = 1
	else:
		maxid = maxid + 1
	material =Material.objects.get(id=request.GET['q'])
	if material.report.name == "LAB":
		field_list = Material.objects.all().filter(report_id = 1)
		if request.method=='POST':
			form1 = JobForm(request.POST)
			form2 = ClientJobForm(request.POST)
			form3 = TestTotalForm(request.POST)
			if form1.is_valid and form2.is_valid() and form3.is_valid():
				def clean_name(self):
					cleaned_data = self.cleaned_data
					pay = cleaned_data.get('pay', '')
					check_number = cleaned_data.get('check_number', '')
					check_dd_date = cleaned_data.get('check_dd_date', '')
					sample = cleaned_data.get('sample', '')
					letter_no = cleaned_data.get('letter_no','')
					other_test = cleaned_data.get('other_test','')
					unit_price = cleaned_data.get('unit_price','')
				profile = form1.save(commit=False)
				profile.job_no = maxid
				profile.ip = request.META.get('REMOTE_ADDR')
				cl = Clientadd.objects.aggregate(Max('id'))
				clientid =cl['id__max']
				clid = Clientadd.objects.get(id = clientid)
				profile.client = clid
				report = Report.objects.get(id=1)
				profile.report_type = report
				profile.save()
				form1.save_m2m()
				test = request.POST.getlist('test')
				profile1 = form2.save(commit=False)		
				profile1.material = material
				jbmx = Job.objects.aggregate(Max('id'))
				jobmax =jbmx['id__max']
				client = Job.objects.get(id =jobmax)
				profile1.job = client
				profile1.save()
				form2.save_m2m()
				profile2 = form3.save(commit=False)
				profile2.job = client
				profile2.save()
				form3.save_m2m()
				return HttpResponseRedirect(reverse('Automation.tcc.views.gen_report_other'))
		else:	
			form1 = JobForm()
			form2 = ClientJobForm()
			form3 = TestTotalForm()
		temp = {"form1": form1,'field_list':field_list,'query':query}
		return render_to_response('tcc/add_job_other_test.html',dict(\
		temp.items()+tmp.items()), context_instance=RequestContext(request))
	else :
		field_list = Material.objects.all().filter(report_id = 2)
		if request.method=='POST':
			form1 = JobForm(request.POST)
			form2 = SuspenceJobForm(request.POST)
			form3 = TestTotalForm(request.POST)
  			if form1.is_valid and form2.is_valid():
				def clean_name(self):
					cleaned_data = self.cleaned_data
					pay = cleaned_data.get('pay', '')
					check_number = cleaned_data.get('check_number', '')
					check_dd_date = cleaned_data.get('check_dd_date', '')
					sample = cleaned_data.get('sample', '')
					letter_no = cleaned_data.get('letter_no','')
					other_test = cleaned_data.get('other_test','')
					unit_price = cleaned_data.get('unit_price','')
				profile = form1.save(commit=False)
				profile.job_no = maxid
				profile.ip = request.META.get('REMOTE_ADDR')
				cl = Clientadd.objects.aggregate(Max('id'))
				clientid =cl['id__max']
				clid = Clientadd.objects.get(id = clientid)
				profile.client = clid
				report = Report.objects.get(id=2)
				profile.report_type = report
				profile.save()
				form1.save_m2m()
				profile1 = form2.save(commit=False)	
				profile1.job_no = maxid	
				profile1.field = material
				jbmx = Job.objects.aggregate(Max('id'))
				jobmax =jbmx['id__max']
				client = Job.objects.get(id =jobmax)
				profile1.job = client
				profile1.save()
				form2.save_m2m()
				profile2 = form3.save(commit=False)
				profile2.job = client
				dist =  Distance.objects.aggregate(Max('id'))
				distid =dist['id__max']
				site = Distance.objects.get(id=distid)
				distance = 2*site.sandy
				if distance < 100:
					rate = 1000
				elif distance == 0:
					rate = 0
				else :
					rate = 10*distance
				profile2.rate = rate
				profile2.save()
				form3.save_m2m()
				return HttpResponseRedirect(reverse('Automation.tcc.views.gen_report_other'))
		else:	
			form1 = JobForm()
			form2 = SuspenceJobForm()
		temp ={"form1": form1,'field_list':field_list,'query':query}
		return render_to_response('tcc/add_job_other_test.html',dict(\
		temp.items() + tmp.items()), context_instance=
		RequestContext(request))

def add_suspence(request):
	"""
	** add_suspence **

	The calculation for the price of the material to be tested is 
	calculated here. The rate for the distance calculated is also
	calculated here and the same is put in the suspence table.
	"""

	mee = SuspenceJob.objects.aggregate(Max('id'))
	minid =mee['id__max']
	client = SuspenceJob.objects.get(id=minid)
	value = SuspenceJob.objects.values_list('test').filter(id=minid)
	values = Test.objects.get(id = value)
	if client.field.name == "Soil for BC":
		a = int(client.other) - 10
		b = int(client.other) - 20
		c = int(client.other) - 30
		if a > 0 and a < 10 and a < 20 and a<30:
			unit_price = a*int(values.cost)+int(values.quantity)
		elif b >= 0 and b < 10 and b <20: 
			unit_price = b*int(values.cost)+int(values.quantity)+9000
		elif c >= 0:
			unit_price = c*int(values.cost)+int(values.quantity)+12000
		else : 
			unit_price =int(client.other)*int(values.cost)+int(values.\
			quantity)
	else:
		unit_price = values.cost
	job = Job.objects.aggregate(Max('id'))
	jobmaxid = job['id__max']
	clients = Job.objects.get(id=jobmaxid)
	price = unit_price*int(clients.sample)
	job = clients
	p = TestTotal(unit_price=price, job=job,)
	p.save()
	dist =  Distance.objects.aggregate(Max('id'))
	distid =dist['id__max']
	site = Distance.objects.get(id=distid)
	distance = 2*site.sandy
	report_type = "Suspence" 
	if distance < 100:
		rate = 1000
	elif distance == 0:
		rate = 0
	else :
		rate = 10*distance
	m = Suspence(rate=rate, sus=client,job=job)
	m.save()
	amt = Amount(job = job ,unit_price=price,report_type = report_type,)
	amt.save()
	return HttpResponseRedirect(reverse('Automation.tcc.views.job_submit'))

def gen_report(request):
	"""
	** gen_report **

	The lab works come here. Then depending upon the mode of payemnt
	of the Job, it is categorised as General Report work or Suspence
	work. The jobs whos mode of payment is cash and has 0 TDS amount
	are called General Report. All the other jobs are categorised as
	Suspence.
	"""
	job = Job.objects.aggregate(Max('id'))
	jobmaxid = job['id__max']
	client = Job.objects.get(id=jobmaxid)
	gen = ClientJob.objects.aggregate(Max('id'))
	genid =gen['id__max']
	clients = ClientJob.objects.get(id =genid)
	value = ClientJob.objects.values_list('test').filter(id=genid)
	values = Test.objects.values_list('cost',flat=True).filter(id__in 
	= value)
	price = sum(values)
	unit_price = price*int(client.sample)
	p = TestTotal(unit_price=unit_price, job=client,)
	p.save()
	if client.pay == "cash" and client.tds == 0:
		report_type = "General_report"
		from Automation.tcc.variable import *
		type =clients.material.distribution.name
		college_income = round(collegeincome * unit_price / 100.00)
		admin_charge = round(admincharge * unit_price / 100.00)
		temp =  unit_price - college_income - admin_charge
		ratio1 = ratio1(type)
		ratio2 = ratio2(type)
		consultancy_asst = round(ratio1 * temp / 100)
		development_fund = round(ratio2 * temp / 100)
		m = Amount(job = client ,unit_price=unit_price,development_fund
		=development_fund, college_income =college_income, admin_charge
		=admin_charge, consultancy_asst=consultancy_asst,report_type = 
		report_type)
		m.save()
	else:
		report_type = "Suspence"
		sus = Suspence(rate=0,job=client)
		sus.save()
		amt = Amount(job = client ,unit_price=unit_price,report_type 
		= report_type,)
		amt.save()
	return HttpResponseRedirect(reverse('Automation.tcc.views.job_submit'))
	
def gen_report_other(request):
	"""
	** gen_report_other **

	For the Jobs whose material or work type doesn't match with all
	that defined in the software, there is an option provided i.e
	other work or material. It means one can himself define the work
	type and amount for it.
	"""
	job = Job.objects.aggregate(Max('id'))
	jobmaxid = job['id__max']
	client = Job.objects.get(id=jobmaxid)
	gen = ClientJob.objects.aggregate(Max('id'))
	genid =gen['id__max']
	clients = ClientJob.objects.get(id =genid)
	testmax = TestTotal.objects.aggregate(Max('id'))
	testmaxid =testmax['id__max']
	testmax_id = TestTotal.objects.get(id =testmaxid)
	unit_price = testmax_id.unit_price
	if client.pay == "CASH" and client.tds == 0:
		report_type = "General_report"
		from Automation.tcc.variable import *
		type =clients.material.distribution.name
		college_income = round(collegeincome * unit_price / 100.00)
		admin_charge = round(admincharge * unit_price / 100.00)
		temp =  unit_price - college_income - admin_charge
		ratio1 = ratio1(type)
		ratio2 = ratio2(type)
		consultancy_asst = round(ratio1 * temp / 100)
		development_fund = round(ratio2 * temp / 100)
		m = Amount(job = client ,unit_price=unit_price,development_fund
		=development_fund, college_income =college_income, admin_charge
		=admin_charge, consultancy_asst=consultancy_asst,report_type 
		= report_type)
		m.save()
	else:
		report_type = "Suspence"
		sus = Suspence(rate=0,job=client)
		sus.save()
		amt = Amount(job = client ,unit_price=unit_price,report_type 
		= report_type,)
		amt.save()
	return HttpResponseRedirect(reverse('Automation.tcc.views.job_submit'))

def job_submit(request):
	"""
	** job_submit **

	The view to ensure that job is successfully saved.
	"""
	if request.user.is_staff == 0 and request.user.is_active == 1 and \
	request.user.is_superuser == 0 :
		use = request.user
		client = UserProfile.objects.get(user_id = use)
		clients = client.id
	if request.user.is_staff == 1 and request.user.is_active == 1 and \
	request.user.is_superuser == 1:
		id = UserProfile.objects.aggregate(Max('id'))
		clients =id['id__max']
	job = Job.objects.aggregate(Max('id'))
	jobmaxid = job['id__max']
	client = Job.objects.get(id=jobmaxid)
	value = client.report_type_id
	jobno = client.job_no
	add = Clientadd.objects.aggregate(Max('id'))    # this is in case one clicks on adding more material into a job
	addid =add['id__max']
	more = Clientadd.objects.get(id=addid)
	moremat = more.client_id
	temp = {'clients':clients,'value':value,'moremat':moremat,'jobno'
	:jobno}
	return render_to_response('tcc/job_submit.html',dict(temp.items() + 
	tmp.items()), context_instance=RequestContext(request))
	
@login_required
def job_ok(request):
	"""
	** job_ok **

	This is to do the calculation of taxes on the total amount of a 
	job. The calculation of tax on an amount depend on several
	factors on which it depend, like tranportation charges, discount,
	tds amount etc.
	"""

	material =request.GET.get('id', '')
	id = Job.objects.aggregate(Max('job_no'))
	maxid =id['job_no__max']
	job_no = maxid
	value =Job.objects.values_list('testtotal__unit_price',flat=True)\
	.filter(job_no=maxid)
	price = sum(value)
	from Automation.tcc.variable import *
	try:
		trans_value = Job.objects.values_list('suspence__rate',flat=\
		True).filter(job_no=maxid)
		trans_total = sum(trans_value)
		discount_value = Job.objects.values_list('discount',flat=True)\
		.filter(job_no=maxid)
		discount_total = sum(discount_value)
		trans_net_total = price + trans_total - discount_total
		service_tax= round(servicetax *  trans_net_total)
		education_tax = round(educationtax *  trans_net_total)
		higher_education_tax = round(highereducationtax *  
		trans_net_total)
		net_total =  trans_net_total + higher_education_tax +\
		education_tax + service_tax
		bal = Job.objects.values_list('tds',flat=True).\
		filter(job_no=maxid)
		tdstotal = sum(bal)
		balance = net_total - tdstotal
		m = Bill(job_no = job_no, price = price, service_tax=service_tax, 
		higher_education_tax = higher_education_tax, education_tax = 
		education_tax, net_total = net_total, balance = 
		balance,trans_total=trans_total,trans_net_total=trans_net_total,
		discount_total=discount_total)
	except Exception:
		discount_value = Job.objects.values_list('discount',flat=True).\
		filter(job_no=maxid)
		discount_total = sum(discount_value)
		trans_net_total = price - discount_total
		service_tax= round(servicetax *  trans_net_total)
		education_tax = round(educationtax *  trans_net_total)
		higher_education_tax = round(highereducationtax *  
		trans_net_total)
		net_total =  trans_net_total + higher_education_tax +\
		education_tax + service_tax
		bal = Job.objects.values_list('tds',flat=True).\
		filter(job_no=maxid)
		tdstotal = sum(bal)
		balance = net_total - tdstotal
		m = Bill(job_no = job_no, price = price, service_tax=service_tax, 
		higher_education_tax = higher_education_tax, education_tax = 
		education_tax, net_total = net_total, balance = balance, 
		discount_total=discount_total,trans_net_total=trans_net_total,)
	m.save()
	amt = Job.objects.filter(job_no=maxid).values('amount__report_type')
	temp = {"maxid":maxid,'amt':amt}
	if request.user.is_staff == 1 and request.user.is_active == 1 and \
	request.user.is_superuser == 1 :
		return render_to_response('tcc/job_ok.html', dict(temp.items() + 
		tmp.items()), context_instance=RequestContext(request))
	else :
		return render_to_response('tcc/client_job_ok.html',dict(temp.\
		items() + tmp.items()), context_instance=RequestContext(request))
	
@login_required
def get_documents(request):
	"""
	** get_documents **

	This shows the different documents once the job is completely 
	filled and is asked to generate bill. Depending upon the type of 
	user the documents are provided to the user. The various documents
	are Receipt, Voucher and Bill.
	"""
	id = Job.objects.aggregate(Max('job_no'))
	maxid =id['job_no__max']
	amt = Job.objects.filter(job_no=maxid).values('amount__report_type')
	temp = {"maxid":maxid,'amt':amt}
	if request.user.is_staff == 1 and request.user.is_active == 1 and \
	request.user.is_superuser == 1 :
		return render_to_response('tcc/job_ok.html', dict(temp.items() 
		+ tmp.items()), context_instance=RequestContext(request))
	else :
		return render_to_response('tcc/client_job_ok.html',dict(temp.\
		items() + tmp.items()), context_instance=RequestContext(request))
		
	
@login_required
def bill(request):
	"""
	** bill **

	This shows the bill in HTML format. All the taxes, amount, materials 
	tested are defined. There are 2 deifferent templates for Gneral
	report and supence works.
	"""

	try :
		job =Job.objects.get(id=request.GET['id'])
	except Exception:
		id = Job.objects.aggregate(Max('id'))
		maxid =id['id__max']
		job = Job.objects.get(id = maxid)
	jobid = job.id
	job_no = job.job_no
	job_date =job.date
	getjob = Job.objects.all().filter(job_no=job_no).values(
	'clientjob__material__name','date','testtotal__unit_price','site',
	'suspencejob__field__name','report_type', 
	'clientjob__material__matcomment_id','suspencejob__field__matcomment_id',
	'sample','letter_no','letter_date', 'suspencejob__other',
	'clientjob__material__id').distinct()
	testname = Job.objects.all().filter(job_no=job_no).values(
	'clientjob__test__name','clientjob__test__material' ).distinct()
	gettest = Job.objects.all().filter(job_no=job_no).values(
	'clientjob__material__test__name','clientjob__material__id',
	'clientjob__material__test__name')
	getadd = Job.objects.all().filter(id = jobid).values(
	'client__client__first_name', 'client__client__middle_name', 
	'client__client__last_name','client__client__address', 
	'client__client__city', 'client__client__company',
	'client__client__state','site',).distinct()
	from Automation.tcc.variable import *
	bill = Bill.objects.get(job_no=job_no)
	matcomment= MatComment.objects.all()
	servicetaxprint = servicetaxprint
	educationtaxprint = educationtaxprint
	highereducationtaxprint = highereducationtaxprint
	net_total1 = bill.net_total
	from Automation.tcc.convert_function import *
	net_total_eng = num2eng(net_total1)
	template = {'job_no': job_no ,'net_total_eng':net_total_eng,
	'servicetaxprint':servicetaxprint,'highereducationtaxprint':
	highereducationtaxprint,'educationtaxprint':educationtaxprint,
	'bill':bill, 'job' : job, 'net_total1' : net_total1, 'getjob' : 
	getjob, 'getadd' : getadd,'job_date':job_date,'gettest':gettest,
	'testname':testname,'matcomment':matcomment}
	amtid = Amount.objects.aggregate(Max('id'))
	amtmaxid =amtid['id__max']
	amt = Amount.objects.get(job_id = jobid)
	if amt.report_type == "General_report" :
		return render_to_response('tcc/bill.html', dict(template.\
		items() + tmp.items()), context_instance = RequestContext(request))
	else :
		return render_to_response('tcc/suspence_bill.html', dict(\
		template.items() + tmp.items()), context_instance = 
		RequestContext(request))

@login_required
def receipt_report(request):
	"""
	** receipt_report **

	View the Receipt In Html format. This shows the material tested 
	for the client and total amount for it.
	"""
	try :
		job =Job.objects.get(id=request.GET['id'])
	except Exception:
		id = Job.objects.aggregate(Max('id'))
		maxid =id['id__max']
		job = Job.objects.get(id = maxid)
	job_no = job.job_no
	jobid =job.id
	job_date = job.date
	client = Job.objects.all().filter(id = jobid).values(
	'client__client__first_name', 'client__client__middle_name', 
	'client__client__last_name','client__client__address', 
	'client__client__city','client__client__company')
	mate = Job.objects.all().filter(job_no=job_no).values(
	'clientjob__material__name','suspencejob__field__name',
	'report_type','date','clientjob__material__matcomment_id',).\
	distinct()
	bill = Bill.objects.get(job_no=job_no)
	matcomment= MatComment.objects.all()
	balance = bill.balance
	net_total_eng = num2eng(balance)
	template = {'mate':mate, 'net_total_eng':net_total_eng,'client':
	client,'bill':bill,'job':job,'job_date':job_date,'matcomment':matcomment}
	return render_to_response('tcc/receipt.html',  dict(template.\
	items() + tmp.items()), context_instance = RequestContext(request))
	
@login_required
def additional(request):
	"""
	** additional **

	This functions displays the additional information that describes
	all the taxes information.
	"""
	job =Job.objects.get(id=request.GET['id'])
	job_no = job.job_no
	from Automation.tcc.variable import *
	bill = Bill.objects.get(job_no=job_no)
	
	template = {'job_no': job_no ,'bill':bill,'servicetaxprint' : servicetaxprint,
	'highereducationtaxprint' : highereducationtaxprint,'educationtaxprint'
	:educationtaxprint}
	return render_to_response('tcc/additional.html',dict(template.items() + tmp.items()), 
	context_instance = RequestContext(request))
		
@login_required
def s_report(request):
	"""
	** s_report **

	This shows the suspence voucher in HTML format. All the taxes, 
	amount, materials tested are defined.
	"""

	try :
		job =Job.objects.get(id=request.GET['id'])
	except Exception:
		id = Job.objects.aggregate(Max('id'))
		maxid =id['id__max']
		job = Job.objects.get(id = maxid)
	jobid = job.id
	job_no = job.job_no
	job_date = job.date
	getjob = Job.objects.all().filter(job_no=job_no).values(
	'clientjob__material__name','testtotal__unit_price','site',
	'suspencejob__field__name','report_type','sample','pay',
	'check_number','check_dd_date','clientjob__material__matcomment_id',
	'suspencejob__field__matcomment_id').distinct()
	matcomment= MatComment.objects.all()
	getadd = Job.objects.all().filter(id = jobid).values(
	'client__client__first_name', 'client__client__middle_name', 
	'client__client__last_name','client__client__address', 
	'client__client__city', 'client__client__state','site','letter_no',
	'letter_date','client__client__company').distinct()
	from Automation.tcc.variable import *
	bill = Bill.objects.get(job_no=job_no)
	
	bal = Job.objects.values_list('tds',flat=True).filter(job_no=job_no)
	tdstotal = sum(bal)
	net_total1 = bill.balance
	from Automation.tcc.convert_function import *
	net_total_eng = num2eng(net_total1)
	template = {'job_no': job_no ,'servicetaxprint' : servicetaxprint,
	'net_total_eng':net_total_eng,'highereducationtaxprint' : 
	highereducationtaxprint,'educationtaxprint':educationtaxprint,
	'bill':bill, 'job' : job, 'jobid':jobid,'getjob' : getjob, 
	'getadd' : getadd,'tdstotal':tdstotal,'job_date':job_date,'matcomment':
	matcomment}
	return render_to_response('tcc/suspence_report.html',dict(template.\
	items() + tmp.items()), context_instance = RequestContext(request))
	
def g_report(request):
	"""
	** g_report **

	g_report Function shows the total vouchers generated in a job.
	"""
	tmp = material_site()
	id = Job.objects.aggregate(Max('job_no'))
	maxid =id['job_no__max']
	amt = Job.objects.filter(job_no = maxid)
	temp =  {'amt':amt}
	return render_to_response('tcc/get_report.html',dict(temp.items() + 
	tmp.items()), context_instance=RequestContext(request))	
	
@login_required	
def rep(request):
	"""
	** rep **

	Rep Function Displays the voucher in html format. This dispays the 
	all the distributions with there amount like college incomee, 
	admincharge, etc.
	"""
	from Automation.tcc.variable import *
	query =request.GET.get('id')
	client = TestTotal.objects.all().get(job_id =query)
	amount = Amount.objects.all().get(job_id =query)
	user = Job.objects.all().get(id=query)
	job = user.job_no
	id = Job.objects.aggregate(Max('id'))
	maxid =id['id__max']
	jobid = Job.objects.get(id = maxid)
	bill = Bill.objects.all().get(job_no=job)
	name = Job.objects.all().filter(id=query).values(\
	'client__client__first_name', 'client__client__middle_name', 
	'client__client__last_name','client__client__address',
	'client__client__city','client__client__company','pay',
	'check_number','check_dd_date','clientjob__material__matcomment_id',
	'suspencejob__field__name') 
	matcomment= MatComment.objects.all()
	try:
		use = ClientJob.objects.all().get(job_id=query)
		mat = use.material.name
		lab = use.material.lab_id
		con_type = use.material.distribution.name
	except Exception:
		use = SuspenceJob.objects.all().get(job_id=query)
		mat = use.field.name
		lab = use.field.lab_id
		con_type = use.field.distribution.name
	staff = Staff.objects.all().filter(lab_id = lab)
	ratio1 = ratio1(con_type)
	ratio2 = ratio2(con_type)
	net_total = amount.unit_price
	from Automation.tcc.convert_function import *
	net_total_eng = num2eng(net_total)
	template = {'net_total_eng' : net_total_eng,'servicetaxprint':
	servicetaxprint,'highereducationtaxprint':highereducationtaxprint,
	'educationtaxprint':educationtaxprint,'client': client,'amount':
	amount,'con_type':con_type, 'ratio1':ratio1, 'ratio2':ratio2, 
	'collegeincome':collegeincome, 'admincharge' : admincharge, 'user'
	:user, 'name':name, 'mat':mat, 'staff':staff,'bill':bill,'job':job,
	'matcomment':matcomment}
	return render_to_response('tcc/report.html', dict(template.items() + 
	tmp.items()), context_instance = RequestContext(request))
	

def transport(request):
	"""
	** transport **

	Transport Function displays the form that get the information like 
	kilometeres travelled etc from the user to get the transportation 
	charges.
	"""
	if request.method == 'POST':
		form = TransportForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			job_no =cd['job_no']
			test_date =cd['test_date']
			kilometer =cd['kilometer']
			date =cd ['date']
			id = Transport.objects.aggregate(Max('id'))
			maxid =id['id__max']
			if maxid== None :
				maxid = 1
			else:
				maxid = maxid + 1
			bill_no = maxid
			#rate = cd ['rate']
			form.save()
			Transport.objects.filter(job_no = job_no).update( bill_no
			= maxid )
			data = {'job_no':job_no,'rate':rate, 'kilometer': kilometer,
			'bill_no':bill_no,'test_date':test_date}
			return render_to_response('tcc/trans.html', dict(data.\
			items()+tmp.items()),context_instance=RequestContext(request))
	else:
		form = TransportForm()
	temp = {'form': form}
	return render_to_response('tcc/client.html', dict(temp.items() + 
	tmp.items()),context_instance=RequestContext(request))

def transport_bill(request):
	"""
	** transport_bill **

	Transport Bill Function generates transport Bill
	"""
	transport_old = Transport.objects.get(job_no=request.GET['job_no'])
	client = ClientJob.objects.get(job_no=request.GET['job_no'])
	kilometer = transport_old.kilometer
	temp = [0,0,0,0,0,0,0,0,0,0]
	range = kilometer.split(',')
	i=0
	while i < len(range):
		temp[i] = range[i]
		i+=1
	rate = transport_old.rate
	amount1 = int(temp[0])*rate
	amount2 = int(temp[1])*rate
	amount3 = int(temp[2])*rate
	amount4 = int(temp[3])*rate
	amount5 = int(temp[4])*rate
	amount6 = int(temp[5])*rate
	amount7 = int(temp[6])*rate
	amount8 = int(temp[7])*rate
	amount9 = int(temp[8])*rate
	amount10 = int(temp[9])*rate
	total = amount1 + amount2 + amount3 + amount4 + amount5 + amount6 
	+ amount7 + amount8 + amount9 + amount10
	all_amounts = amount1,amount2,amount3,amount4,amount5,amount6,
	amount7,amount8,amount9,amount10
	Transport.objects.filter(job_no = transport_old.job_no).update(\
	total = total, amounts = all_amounts )
	transport = Transport.objects.get(job_no=transport_old.job_no)
	title = get_object_or_404(Variable, pk='1')
	sub_title = get_object_or_404(Variable, pk='2')
	sign = get_object_or_404(Variable, pk='3')
	vehical_no = get_object_or_404(Variable, pk='4')
	template ={'transport':transport, 'title':title, 'sub_title':
	sub_title, 'vehical_no':vehical_no, 'client':client, 'sign':sign}
	return render_to_response('tcc/transportbill.html',dict(template.\
	items() + tmp.items()) , context_instance=RequestContext(request))

@login_required
def ta_da(request):
	"""
	** ta_da **

	Ta_Da Function displays the form for filling the Transport and Daily 
	Allowance charges for a Job.
	"""
	query = request.GET.get('q', '')
	try :
		sus = Suspence.objects.get(job=query)
	except Exception:	
		sus =[]
	if request.method == 'POST':
		form = TadaForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			test_date =cd['test_date']
			end_date =cd['end_date']
			reach_site =cd['reach_site']
			profile = form.save(commit=False)
			jobid = Job.objects.get(id=query)
			profile.job = jobid
			profile.save()
			return HttpResponseRedirect(reverse(\
			'Automation.tcc.views.tada_view'))
	else:
		form = TadaForm()
	temp = {'form': form,'query':query,'sus':sus}
	return render_to_response('tcc/suspenceclear.html', dict(temp.\
	items() + tmp.items()), context_instance=RequestContext(request))

def tada_view(request):
	"""
	** tada_view **
	Tada_view function confirms that tada is saved.
	"""
	id = TaDa.objects.aggregate(Max('id'))
	maxid =id['id__max']
	tada = TaDa.objects.all().get(id=maxid)
	data = {'tada':tada }			
	return render_to_response('tcc/tada_ok.html', dict(data.items() + 
	tmp.items()), context_instance=RequestContext(request))

def ta_da_bill(request):
	"""
	** ta_da_bill **

	Report of TA/DA Bill For Particular Date.
	"""
	tada = TaDa.objects.get(job=request.GET['job'],test_date=request.\
	GET['test_date'])
	job = Job.objects.get(id=request.GET['job'])
	c = job.id
	client = Job.objects.filter(id=c).values('client__client__first_name')
	lab_staff = tada.testing_staff_code
        t1=0
        temp = [0,0,0,0,0,0,0,0,0,0]
	range = lab_staff.split(',')
	i=0
	while i < len(range):
		temp[i] = range[i]
		i+=1
	amount1 = temp[0]
	amount2 = temp[1]
	amount3 = temp[2]
	amount4 = temp[3]
	amount5 = temp[4]
	amount6 = temp[5]
	amount7 = temp[6]
	amount8 = temp[7]
	amount9 = temp[8]
	amount10 = temp[9]
	
	staff =Staff.objects.all().filter(Q(code=amount1)| Q(code=amount2) 
	| Q(code=amount3) | Q(code=amount4) | Q(code=amount5) | Q(code=\
	amount6) | Q(code=amount7)| Q(code=amount8) | Q(code=amount9) | 
	Q(code=amount10)).order_by('id') 
	daily_income = Staff.objects.filter(Q(code=amount1)| Q(code=\
	amount2) | Q(code=amount3) | Q(code=amount4) | Q(code=amount5) | 
	Q(code=amount6) | Q(code=amount7)| Q(code=amount8)| Q(code=amount9) 
	| Q(code=amount10)).aggregate(Sum('daily_income'))
	daily = int(daily_income['daily_income__sum']) 
	TaDa.objects.filter(job = tada.job).update( tada_amount = daily )
	data = {'tada':tada,'job':job,'staff':staff,  'daily':daily,
	'client':client}
	return render_to_response('tcc/ta_da_bill.html', data , 
	context_instance = RequestContext(request))

def distance(request):
	"""
	** distance **

	Distance Function is for calculation of distance of the site on 
	the map. This displays a form fo filling the site.
	"""
	mee = Job.objects.aggregate(Max('id'))
	jobid =mee['id__max']
	if jobid== None :
		jobid = 1
	else:
		jobid = jobid +1
	if request.method =='POST':
		form = DistanceForm(request.POST)
  		if form.is_valid():
			cd = form.cleaned_data
			sandy = cd['sandy']
			profile = form.save(commit=False)
			profile.job = jobid
			profile.save()
			return render_to_response('tcc/map_ok.html',tmp, 
			context_instance = RequestContext(request))
	else:
  		form = DistanceForm()
	return render_to_response('tcc/siteinmap.html', {"form": form,}, 
	context_instance=RequestContext(request))

def clientreport(request):
	"""
	** clientreport **

	Retrieves out the bill or receipt on demand for a particular job.
	"""
	query =request.GET.get('q', '')
	if query:
		job = Job.objects.filter(job_no = query).values('id', 
		'client__client__first_name', 'client__client__address', 
		'client__client__city', 'clientjob__material__name',
		'report_type', 'suspencejob__field__name', 'site', 
		'testtotal__unit_price','amount__report_type').order_by('id').distinct()
		amt = Job.objects.filter(job_no=query).values(\
		'amount__report_type')
		bill = Bill.objects.filter(job_no=query)
		temp = {'job':job,'query':query,'amt':amt,'bill':bill}
	else:	
		job =[]
		temp = {'job':job,'query':query,}
	return render_to_response('tcc/clientreport.html',dict(temp.items() 
	+ tmp.items()),context_instance=RequestContext(request))
	
def suspence_clearance(request):
	"""
	** suspence_clearance **

	Suspence Clearance Function clears the suspence work. It has the 
	form for filling the extra charges. 
	"""
	query = request.GET.get('q', '')
	try :
		sus = Suspence.objects.get(job=query)
	except Exception:	
		sus =[]
	if request.method == 'POST':
		form = SuspenceClearence(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			labour_charge =cd['labour_charge']
			car_taxi_charge =cd['car_taxi_charge']
			boring_charge_external=cd['boring_charge_external']
			boring_charge_internal=cd['boring_charge_internal']
			lab_testing_staff=cd['lab_testing_staff']
			field_testing_staff =cd['field_testing_staff']
			job =query
			Suspence.objects.filter(job = job).update(labour_charge = 
			labour_charge, boring_charge_external=boring_charge_external, 
			boring_charge_internal = boring_charge_internal, 
			field_testing_staff = field_testing_staff, car_taxi_charge 
			= car_taxi_charge, lab_testing_staff = lab_testing_staff)
			data = {'job_no' : job, 'labour_charge':labour_charge, 
			'boring_charge_external' : boring_charge_external,
			'boring_charge_internal' : boring_charge_internal, 
			'car_taxi_charge' : car_taxi_charge, 'lab_testing_staff' : 
			lab_testing_staff, 'sus':sus,}
			return render_to_response('tcc/suspence_clearence_ok.html', 
			dict(data.items() + tmp.items()), context_instance=
			RequestContext(request))
	else:
		form = SuspenceClearence()
	temp ={'form': form,'query':query,'sus':sus}
	return render_to_response('tcc/suspenceclear.html', dict(temp.items() + 
	tmp.items()), context_instance=RequestContext(request))

@login_required

#def search(request):	
#	** search **
#
#	Search Function is used to search a client using his/her name, 
#	type of work and address. The 'icontain' keyword is used which 
#	fetches all the rows that contain the query. THen the data related 
#	to that client that is required is also enlisted.
#	
#	query=request.GET.get('q', '')
#	addquery=request.GET.get('add', '')
#	if query:
#		qset = (
#			Q(first_name__icontains=query) |
#			Q(middle_name__icontains=query) |
#			Q(last_name__icontains=query)
#			
#	   	)	
#		aset = (
#	     	Q(address__icontains=addquery)|
#			Q(city__icontains=addquery)
#		)
#		results = UserProfile.objects.filter(aset).filter(qset).\
#		distinct()
#	else:
#		results = []
#	temp = {'results': results,'query': query,}
#	return render_to_response("tcc/search.html", dict(temp.items() + 
#	tmp.items()),context_instance=RequestContext(request))




#def search_helper(query):
#        import itertools
#        results =UserProfile.objects.filter(first_name__icontains=query)
#        return (results.distinct())
#        return render_to_response('tcc/search.html', {'searchform':SearchForm()})
#for L in range(1, count+1):
#                for subset in itertools.permutations(words, L):
#                        count1=1
#                        query1=subset[0]
#                        while count1!=len(subset):
#                                query1=query1+" "+subset[count1]
#                                count1+=1
#                        model_list = entry_list | UserProfile.objects.filter(first_name__icontains=query1)


def search(request):
    query = ''
    results = None
    if ('q' in request.GET):
        query = request.GET['q']
    results=UserProfile.objects.filter(first_name__istartswith=query)
    #results=UserProfile.objects.exclude(first_name='').filter(first_name__istartswith=query)
    #results=UserProfile.objects.filter(where=["DIFF SOUNDEX(first_name), SOUNDEX(%s))"])
    return render_to_response('tcc/search.html',
                          { 'results': results,'query':query, },context_instance=RequestContext(request))
    #results=UserProfile.objects.raw('SELECT id, first_name, last_name FROM tcc_')
    #results=UserProfile.objects.filter(first_name__istartswith="H")
    #results= Q(first_name__startswith='%') | Q(address__startswith='%')

    

#    if ('q' in request.GET) and request.GET['q'].strip():
#        query = request.GET['q']
        
        #addquery = request.GET['add']
        
#        results = UserProfile.objects.filter()
#    return render_to_response('tcc/search.html',
#                          { 'results': results,'query':query, },
#                          context_instance=RequestContext(request))

#def search( request ):

#    if request.is_ajax():
#        query = request.GET.get( 'q' )
#        if query is not None:            
#            results = UserProfile.objects.filter( 
#                Q( first_name__contains = query ) |
#                Q( last_name__contains = query ) |
#                Q( username__contains = query ) ).order_by( 'first_name' )

#            return HttpResponseRedirect( 'tcc/search.html', { 'results': results, 'query':query, })
def suspence_clearence_report(request):
	"""
	** suspence_clearance_report **

	This function generates the report for the suspence job after 
	clearing it. Here the split function splits out the staff code 
	entry to fetch its name from the tables.
	"""
	suspence = Suspence.objects.get(job=request.GET['job_no'])
	amount = Amount.objects.get(job=request.GET['job_no'])
	try:
		suspencejob = SuspenceJob.objects.get(job=request.GET['job_no'])
		con_type = suspencejob.field.distribution.name
	except Exception:
		suspencejob = ClientJob.objects.get(job=request.GET['job_no'])
		con_type = suspencejob.material.distribution.name
	client =Job.objects.get(id=request.GET['job_no'])
	clientname = Job.objects.filter(id=client.id).values(\
	'client__client__first_name',
	'suspencejob__field__name')
	lab_staff = suspence.lab_testing_staff
        t1=0
        temp = [0,0,0,0,0,0,0,0,0,0]
	range = lab_staff.split(',')
	i=0
	while i < len(range):
		temp[i] = range[i]
		i+=1
	amount1 = temp[0]
	amount2 = temp[1]
	amount3 = temp[2]
	amount4 = temp[3]
	amount5 = temp[4]
	amount6 = temp[5]
	amount7 = temp[6]
	amount8 = temp[7]
	amount9 = temp[8]
	amount10 = temp[9]
	
	field_staff = suspence.field_testing_staff
	temp = [0,0,0,0,0,0,0,0,0,0]
	range = field_staff.split(',')
	i=0
	while i < len(range):
		temp[i] = range[i]
		i+=1
	amounts1 = temp[0]
	amounts2 = temp[1]
	amounts3 = temp[2]
	amounts4 = temp[3]
	amounts5 = temp[4]
	amounts6 = temp[5]
	amounts7 = temp[6]
	amounts8 = temp[7]
	amounts9 = temp[8]
	amounts10 = temp[9]
	staff =Staff.objects.all().filter(Q(code=amount1)|Q(code=amount2) 
	| Q(code=amount3) | Q(code=amount4) | Q(code=amount5) | Q(code=
	amount6) | Q(code=amount7)| Q(code=amount8)| Q(code=amount9) | \
	Q(code=amount10)| Q(code=amounts1)| Q(code=amounts2) | Q(code=
	amounts3) | Q(code=amounts4) | Q(code=amounts5) | Q(code=amounts6) 
	| Q(code=amounts7)| Q(code=amounts8)| Q(code=amounts9) | Q(code=
	amounts10)).order_by('id')
	temp = suspence.labour_charge + suspence.rate + suspence.\
	boring_charge_external
	+ suspence.car_taxi_charge
	balance= amount.unit_price - (temp + suspence.boring_charge_internal)
	from Automation.tcc.variable import *
	college_income = round(collegeincome * balance / 100.00)
	admin_charge = round(admincharge * balance / 100.00)
	work_charge = round(workcharge * balance / 100.00)
	balance_temp = balance - college_income - admin_charge -work_charge
	ratio1 = ratio1(con_type)
	ratio2 = ratio2(con_type)
	consultancy_asst = round(ratio1 * balance_temp / 100)
	development_fund = round(ratio2 * balance_temp / 100)
	net_total1 = amount.unit_price
	net_balance_eng = num2eng(net_total1)
	retrieve()
	Suspence.objects.filter(job = client).update( work_charge = 
	work_charge)
	Amount.objects.filter(job = client).update( college_income = 
	college_income, admin_charge = admin_charge, consultancy_asst = 
	consultancy_asst, development_fund = development_fund )
	sus = Suspence.objects.get(job=request.GET['job_no'])
	data = {'transport' : transport, 'net_balance_eng' : 
	net_balance_eng, 'teachers' : staff, 'servicetaxprint' : 
	servicetaxprint, 'highereducationtaxprint':highereducationtaxprint, 
	'educationtaxprint' : educationtaxprint, 'ratio1' : ratio1, 
	'job_no' :client.job_no , 'ratio2' : ratio2, 'other' : temp, 
	'collegeincome' : collegeincome, 'admincharge' : admincharge, 
	'client' : client, 'amount' : amount, 'suspence' : sus, 'client' : 
	client, 'clientname' : clientname}
	return render_to_response('tcc/suspence_clearence_report.html', 
	dict(data.items() + tmp.items()) , context_instance=
	RequestContext(request))
	
def prevwork(request):
	"""
	** prevwork **

	Prevwork function is used to list down all the previous jobs for 
	the client that was searched using search function. It also states 
	which suspence job is cleared and which is still to be cleared, 
	thus requiring the link to clear that job. The values with double 
	underscore indicates that foreign key values are fetched.		
	"""
	user = UserProfile.objects.get(id=request.GET['id'])
	client = user.id
	job = Job.objects.filter(client__client__id = client).values(
	'clientjob__material__name', 'suspencejob__field__name', 'id', 
	'job_no', 'date', 'site',	'amount__report_type', 'report_type', 
	'amount__college_income')
	data = {'user':user, 'job':job,}
	return render_to_response('tcc/prevwork.html',dict(data.items() + 
	tmp.items()), context_instance=RequestContext(request))
	
def clearjob(request):
	"""
	** clearjob **

	Clearjob Function points to the job that is to be cleared listing 
	all the necessary data that is required to be filled. 
	"""

	user = Job.objects.get(id=request.GET['job_id'])
	job = user.id
	temp = {'job':job}
	return render_to_response('tcc/compwork.html',dict(temp.items() 
	+ tmp.items()), context_instance=RequestContext(request))



def contact(request):
	"""
	** contact **

	The contact function defines the contact form that is to be filled
	and emailed	by user to give the feedback or to define the problem.
	"""
	form = ContactForm()
	if request.method == 'POST':
		form = ContactForm(request.POST)
        if form.is_valid():
			cd = form.cleaned_data
			send_mail(
				cd['subject'],
				cd['message'],
				cd.get('email', 'noreply@example.com'),
				['mkaurkhalsa@gmail.com'],
			)
			template = {'form': form}
			return render_to_response('contact/thanks.html',
			dict(template.items() + tmp.items()), context_instance=
			RequestContext(request))
	else:
		form = ContactForm()
	temp ={'form': form}
	if request.user.is_staff == 1 and request.user.is_active == 1 and \
	request.user.is_superuser == 1:
		return render_to_response('contact/contact.html', dict(temp.\
		items() + tmp.items()), context_instance=RequestContext(request))
	elif request.user.is_staff == 0 and request.user.is_active == 1 and \
	request.user.is_superuser == 0 :
		return render_to_response('contact/contact1.html', dict(temp.\
		items()+tmp.items()), context_instance=RequestContext(request))
	else:
		return render_to_response('contact/contact2.html', dict(temp.\
		items()+tmp.items()), context_instance=RequestContext(request))

def registered_user(request):
	user_list=UserProfile.objects.all()
	temp = {'user_list': user_list}
	return render_to_response("tcc/registered_user.html", dict(temp.items() + 
	tmp.items()),context_instance=RequestContext(request))
#	return render_to_response('tcc/registered_user.html',{'user_list':user_list})

import re

from django.db.models import Q

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query	

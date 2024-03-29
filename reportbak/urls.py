"""
File contains urls of the Report
"""
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template

"""
Urls of views.py
"""
urlpatterns = patterns('Automation.report.views',
	(r'^report/$', 'report'),
	(r'^chemical_analysis/$', 'chemical_analysis'),
	(r'^result_chem/$', 'result_chem'),
	(r'^result_cube/$', 'result_cube'),
	(r'^index/$', 'index'),
	(r'^water_test/$', 'water_test'),
	(r'^result_water/$', 'result_water'),
	(r'^brick_test/$', 'brick_test'),
	(r'^result_brick/$', 'result_brick'),
	(r'^soil_ohsr/$', 'soil_ohsr'),
	(r'^result_Soil_ohsr/$', 'result_Soil_ohsr'),
	(r'^soil_building/$', 'soil_building'),
	(r'^result_soil_building/$', 'result_soil_building'),
	(r'^admixture/$', 'admixture'),
	(r'^result_Admixture/$', 'result_Admixture'),
	(r'^cement_ppc/$', 'cement_ppc'),
	(r'^result_Cement_PPC/$', 'result_Cement_PPC'),
	(r'^cement_opc_33/$', 'cement_opc_33'),
	(r'^result_Cement_OPC_33/$', 'result_Cement_OPC_33'),
	(r'^cement_opc_43/$', 'cement_opc_43'),
	(r'^result_Cement_OPC_43/$', 'result_Cement_OPC_43'),
	(r'^cement_opc_53/$', 'cement_opc_53'),
	(r'^result_Cement_OPC_53/$', 'result_Cement_OPC_53'),
	(r'^drink_water/$', 'drink_water'),
	(r'^result_Drinking_water/$', 'result_Drinking_water'),
	(r'thanks$',  direct_to_template, {'template': 'report/thanks.html'}),
)

"""
Urls of search.py
"""
urlpatterns += patterns('Automation.report.search',
	(r'^search_report/$', 'search_report'),
	(r'^search/$', 'search'),
	(r'^report_gen/$', 'report_gen'),
)	

"""
Urls of pdf.py

urlpatterns += patterns('Automation.report.pdf',
	(r'^report_pdf/$', 'report_pdf'),
)
"""


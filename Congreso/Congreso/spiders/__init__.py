# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy
import json

class CongresoSpider(scrapy.Spider):
	name = "Congreso"
	paginaNumero = 0
	numLey = 0
	JSONdata = {}
	JSONleyes = {}
	filename = 'proyleyes.json'
	filename2 = 'proyleyes_detalle.json'

	def start_requests(self):
	#'http://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2016.nsf/Local%20Por%20Numero%20Inverso?OpenView'
		Url = "http://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2016.nsf/Local%20Por%20Numero%20Inverso?OpenView&Start="
		for i in range(0,17):
			urlcong = Url + str(i*100+1)
			yield scrapy.Request(url= urlcong , callback=self.parse)

	def appendJSON(self, data, appendTo):
		for d in data:
			appendTo[len(appendTo)] = data[d]

	def closed(self, reason):
		with open(self.filename, 'a+') as f:
			json.dump(self.JSONdata, f, ensure_ascii=False, indent=2)
		with open(self.filename2, 'a+') as f:
			json.dump(self.JSONleyes, f, ensure_ascii=False, indent=2)

	def parse(self, response):
		if response.status!=200:
			print("")
			print ("[ Error status:"+str(response.status)+" ] URL: " + response.url)
			print("")
			return
		tabla = response.xpath("//body//form//table//tr//td//text()").extract()
		i = 0
		objCount = 0
		obj = {}
		obj[objCount] = {}
		for t in tabla:
			if not len(t)>2:
				break
			if i%5==0 and t[0:1].isdigit():
				obj[objCount]['numero'] = t
			if i%5==1 and t[0:1].isdigit():
				obj[objCount]['fechaUltimaActualizacion'] = t
			if i%5==2:
				if t[0:1].isdigit():
					obj[objCount]['fechaPresentacion'] = t
				else:
					obj[objCount]['fechaPresentacion'] = obj[objCount]['fechaUltimaActualizacion']
					obj[objCount]['fechaUltimaActualizacion'] = ""
					obj[objCount]['estado'] = t
					i += 1
			if i%5==3 and not t[0:1].isdigit():
				obj[objCount]['estado'] = t
			if i%5==4 and not t[0:1].isdigit():
				obj[objCount]['titulo'] = t
				objCount += 1
				obj[objCount] = {}
			i+=1
		self.appendJSON(obj, self.JSONdata)
		linkLeyes = response.xpath("//body//form//table//tr//td//font//a/@href").extract()
		for link in linkLeyes:
			yield scrapy.Request(url='http://www2.congreso.gob.pe'+link , callback=self.parse_proyecto)

	def parse_proyecto(self, response):
		if response.status!=200:
			print("")
			print ("[ Error status:"+str(response.status)+" ] URL: " + response.url)
			print("")
			return
		obj = {}
		obj[0] = {}
		obj[0]['CodIni'] = response.xpath("//body//form//input[@name='CodIni']//@value").extract_first()
		obj[0]['TitIni'] = response.xpath("//body//form//input[@name='TitIni']//@value").extract_first()
		obj[0]['SumIni'] = response.xpath("//body//form//input[@name='SumIni']//@value").extract_first()
		obj[0]['NombredelGrupoParlamentario'] = response.xpath("//body//form//input[@name='NombredelGrupoParlamentario']//@value").extract_first()
		obj[0]['NomCongre_mail'] = response.xpath("//body//form//input[@name='NomCongre_mail']//@value").extract_first()
		obj[0]['DesLegis'] = response.xpath("//body//form//input[@name='DesLegis']//@value").extract_first()
		obj[0]['NumLey'] = response.xpath("//body//form//input[@name='NumLey']//@value").extract_first()
		obj[0]['CodIni_web'] = response.xpath("//body//form//input[@name='CodIni_web']//@value").extract_first()
		self.appendJSON(obj, self.JSONleyes)
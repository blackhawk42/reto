import numpy as np
from numpy import linalg
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

import csv

from string import Template
import urllib.parse

import sys
import os
import os.path

NO_CAR = 'Sin carro'
NO_CAR_EQUIVALENTS = ('No tengo carro', 'No tenía carro')

def ensure_dir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

def getInputPath():
	filetypes = []

	filetypes.append( ('Archivo CSV', '*.csv') )
	title = 'Seleccione el archivo CSV'
	
	filetypes.append( ('Todos los archivos', '*') )
	
	
	return filedialog.askopenfilename(initialdir=os.getcwd(),
											title=title,
											filetypes=filetypes)

def near(a, b, rtol=1e-5, atol=1e-8):
	return np.abs(a-b)<(atol+rtol*np.abs(b))

if __name__ == '__main__':
	mainWin = tk.Tk()
	mainWin.withdraw()
	
	messagebox.showinfo('Archivo CSV', 'Por favor, seleccione el archivo CSV')
	
	# Archivo de trabajo
	entradaPath = getInputPath()
	
	# Si es cancelado
	if entradaPath == '':
		messagebox.showerror('Cancelado', 'Operación cancelada. Saliendo')
		sys.exit(0)
	
	matrix = None
	
	# Tabla de frecuencias. Basicamente, la llave es el "actual" (lo que
	# llamamos "anterior" en la encuesta) y contiene una lista
	# con cada elemento que, nuestra encuesta dice, fue el "siguiente"
	# que se uso cada vez que el actual en turno fue usado (en la
	# encuesta este es el "actual"). Como los elementos siguientes
	# se repiten en proporcion a como fueron usados, tenemos escencialmente
	# una tabla de frecuencias.
	frecuencias = {}
	
	# Marcas sin repetir, con un numero asociado para "traducir" al trabajar
	# con arreglos
	marcasIndex = 0
	marcas = {}
	
	with open(entradaPath, newline='', encoding='utf-8') as f:
		reader = csv.reader(f)
		
		firstline = True
		for row in reader:
			if firstline:
				firstline = False
				continue
			
			last = NO_CAR
			actual = NO_CAR
			
			if row[2].strip() not in NO_CAR_EQUIVALENTS:
				last = row[2].strip()
			
			if row[1].strip() not in NO_CAR_EQUIVALENTS:
				actual = row[1].strip()
			
			# Registrar la marca si no la aviamos visto antes
			# Sólo registraremos las marcas en el "anterior", para evitar
			# columnas que sumen a 0
			try:
				marcas[last]
			except KeyError:
				marcas[last] = marcasIndex
				marcasIndex += 1
			
			
			# Actualizar la tabla de frecuencias
			try:
				# Agregamos el elemento actual a la lista de "siguientes"
				# eslabones
				if actual in marcas: # Dificil de evitar a este punto
					frecuencias[last].append(actual)
				
				# Un KeyError significa que el elemento esta siendo puesto
				# en el diccionario por primera vez. Lo preparamos poniendole
				# una lista con su primer elemento. Esto es, se supone,
				# mas eficiente.
			except KeyError:
				frecuencias[last] = [actual]
	
	# Reiniciamos la cuenta de marcas, para que solo tengan las que realmente hay
	marcas = {}
	indices = {}
	marcasIndex = 0
	for marca in frecuencias:
		marcas[marca] = marcasIndex
		indices[marcasIndex] = marca
		marcasIndex += 1
	
	
	matrix = np.zeros( (len(marcas), len(marcas)) )
	
	for marca in marcas:
		try:
			frecuenciasFila = {}
			
			for siguiente in frecuencias[marca]:
				try:
					frecuenciasFila[siguiente] += 1
				except KeyError:
					frecuenciasFila[siguiente] = 1
			
			
			for siguiente in frecuenciasFila:
				matrix[ marcas[marca] ][ marcas[siguiente] ] = frecuenciasFila[siguiente] / len(frecuencias[marca])
			
		
		# Si la marca no esta como llave ("anterior") en nuestra
		# tabla de frecuencias, simplemente la ignoramos y se queda
		# como una fila sumando a 0 (*nota: preguntar al maestro)
		except KeyError:
			continue
	
	
	#-----------------------| Operaciones principales |----------------|
	
	messagebox.showinfo('Reporte', 'Por favor seleccione la carpeta en la que crear el reporte')
	REPORT_ROOT = filedialog.askdirectory()
	
	if REPORT_ROOT == '':
		saveMatrix(matrix, binaryMarkov=binaryMarkov)
		sys.exit(0)
		
	
	ensure_dir( os.path.join(REPORT_ROOT, 'img') )
	
	## Steady vector
	
	# Obtener el steady state de la mtriz. Si nuestro modelo de Markov es
	# realmente estocastico, este tiende a ciertas probabilidades conforme
	# avanzan los pasos. Esto se puede ver como resolver pM = p, donde M es
	# la matriz de Markov y p = [x_1, x_2, x_3, ..., x_n] donde n es el numero
	# de estados. Despues recodamos que sum(x_1, x_2, x_3, ..., x_n) = 1 y tenemos
	# una bonita serie de ecuaciones perfectamente resolvibles. Esta es la
	# forma mas simple de visualizarlo
	#
	# Por otro lado, y la version que se usa aqui, podemos simplemente verlo
	# como el eigenvector de la matriz con eigenvalor 1. Se usa este
	# metodo no porque no entendamos como hacerlo con el otro (como
	# demuestra nuestra explicacion), simplemente porque numpy ya
	# provee las operaciones para hacerlo eficientemente. Este codigo
	# ya es lo suficientemente grande y ambriento de recursos como
	# esta ahora, ni hablar de que pasara cuando se quieran usar *verdaderas*
	# tablas de datos...
	
	D, V = linalg.eig(matrix)
	
	V = V.T
	
	for val, vec in zip(D, V):
		assert np.allclose(np.dot(matrix, vec), val*vec)
	
	steady_vector = V[near(D, 1.0)][0]
	
	# Labels para los graficos
	labels = sorted(marcas, key=lambda marca: marcas[marca])
	
	plt.pie(steady_vector, labels=labels, autopct='%1.1f%%')
	plt.savefig( os.path.join(REPORT_ROOT, 'img', 'alalarga.png') )
	
	# Migracion: A donde van los clientes de cada marca
	plantillaDict = {'migracion': ''}
	
	for i, row in enumerate(matrix):
		plantillaDict['migracion'] += '\n<h3>Marca: {}</h3>\n'.format(indices[i])
		
		imgPath = os.path.join( os.path.basename(REPORT_ROOT), 'img', '{}-migracion.png'.format( indices[i] ) )
		
		relevant = np.where(row != 0)
		
		rowLabels = []
		for i in relevant[0]:
			rowLabels.append(indices[i])
		
		plt.clf()
		plt.pie(row[relevant], labels=rowLabels, autopct='%1.1f%%')
		plt.savefig( os.path.join(os.path.dirname(REPORT_ROOT), imgPath) )
		
		plantillaDict['migracion'] += '<center><img src=img/{}></center>\n'.format( urllib.parse.quote_plus(os.path.basename(imgPath)) )
	
	
	# Create report html
	with open( os.path.join('templates', 'html', 'reporte.html') ) as templateF:
		template = Template(templateF.read())
		
		with open( os.path.join(REPORT_ROOT, 'reporte.html'), 'w' ) as fout:
			fout.write( template.substitute(plantillaDict) )
	
	

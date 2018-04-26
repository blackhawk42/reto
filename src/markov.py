import numpy as np

import csv
from pprint import pprint

NO_CAR = 'Sin carro'
NO_CAR_EQUIVALENTS = ('No tengo carro', 'No tenía carro')

if __name__ == '__main__':
	
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
	
	with open('respuestas.csv', newline='', encoding='utf-8') as f:
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
			try:
				marcas[last]
			except KeyError:
				marcas[last] = marcasIndex
				marcasIndex += 1
			
			try:
				marcas[actual]
			except KeyError:
				marcas[actual] = marcasIndex
				marcasIndex += 1
			
			
			# Actualizar la tabla de frecuencias
			try:
				# Agregamos el elemento actual a la lista de "siguientes"
				# eslabones
				frecuencias[last].append(actual)
				
				# Un KeyError significa que el elemento esta siendo puesto
				# en el diccionario por primera vez. Lo preparamos poniendole
				# una lista con su primer elemento. Esto es, se supone,
				# mas eficiente.
			except KeyError:
				frecuencias[last] = [actual]
	
	
	pprint(marcas)
	pprint(frecuencias)
	
	
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
	
	print(matrix)
	

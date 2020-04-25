import json
import random
import colorama
import unidecode
import time
import math
from colorama import Fore, Style


class Entry():
	def __init__(self, it, es):
		self.it = it
		self.es = es
	def __repr__(self):
		return self.it + " -> " + self.es

class Player():

	def start(self):
		self._entries = self.entries()
		self._status = self.status()
		self.process_news()
		self.save()

	def entries(self):
		with open("words.txt") as f:
			lines = f.read().splitlines()
			res = []
			for l in lines:
				l = l.split("-")
				l[0] = l[0].strip()
				l[1] = l[1].strip()
				res.append(Entry(l[0], l[1]))
			return res


	def status(self):
		with open("status.json") as f:
			data = json.load(f)
			return data

	# Chequea las palabras en entries
	# pero no en status
	def process_news(self):
		for e in self._entries:
			self._status[e.it]["trans"] = e.es
			if e.it not in self._status:
				self._status[e.it] = dict()
				self._status[e.it]["last"] = None

	def update_weights(self):
		for word, d in self._status.items():
			if "last" in d and d["last"] is not None:
				t = (time.time() - d["last"]) / 86400
				score = 100/(2*t + 1)
			else:
				score = 0
			
			d["score"] = score

	def save(self):
		# Actualizar pesos
		self.update_weights()

		# Escribir en archivo
		with open("status.json", "w") as f:
			f.write(json.dumps(self._status, indent=4))

	def random_entry(self):
		# Create pairs weight - words
		words = []
		weights = []

		for word, d in self._status.items():
			score = d["score"]
			words.append(word)
			weights.append(100 - score)

		return random.choices(population = words, weights = weights)[0]



	def play(self, it2es = True):
		re = self.random_entry()
		entrada = [x for x in self._entries if x.it == re][0]
		mi_estatus = self._status[re]

		print("> " + ("🇮🇹  " if it2es else "🇪🇸  ") + Style.BRIGHT + Fore.BLUE + (re if it2es else entrada.es) + Style.RESET_ALL)

		correcto = entrada.es
		correcto_sin = unidecode.unidecode(correcto)
		
		resp = input()
		resp_sin = unidecode.unidecode(resp)

		# Correcto
		if (it2es and correcto_sin == resp_sin) or (not it2es and resp_sin == unidecode.unidecode(re)): 
			print("\t\t\t" + Style.BRIGHT + Fore.GREEN + "OK" + Style.RESET_ALL)

			mi_estatus["last"] = time.time()

		# Incorrecto
		else:
			print("\t\t\t" + (correcto if it2es else re))
			print("\t\t\t" + Style.BRIGHT + Fore.RED + "WRONG" + Style.RESET_ALL)
			
			mi_estatus["last"] = time.time() - 86400		

		self.save()

if __name__ == "__main__":
	p = Player()
	p.start()
	while True:
		p.play(True)
		p.play(False)
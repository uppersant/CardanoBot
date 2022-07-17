from cardano.backends.walletrest import WalletREST
from cardano.wallet import WalletService, Wallet
from random_word import RandomWords
from colorama import init, Fore
from mnemonic import Mnemonic
import pymongo
import random
import time
import os


class CardanoTools:
	def create_wallet(self):
		mnemonic = Mnemonic("english").generate(strength=256)
		wallet = WalletService(WalletREST(port=8090)).create_wallet(
			name=RandomWords().get_random_word(),
			mnemonic=mnemonic,
			passphrase=str(random.randrange(100000, 1000000)),
		)

		return wallet, mnemonic

	def get_wallet(self, wallet_id):
		return Wallet(wallet_id, backend=WalletREST(port=8090)).balance()

	def create_transaction(self, from_wallet, to_wallet, amount, passphrase):
		return Wallet(from_wallet, backend=WalletREST(port=8090)).transfer(to_wallet, amount, passphrase=passphrase)

	def estimate_transaction(self, from_wallet, to_wallet, amount):
		return Wallet(from_wallet, backend=WalletREST(port=8090)).estimate_fee((to_wallet, Decimal(amount)))


class MongoTools:
	def __init__(self):
		self.wallets = pymongo.MongoClient("mongodb://localhost:27017/")["test"]["wallets"]

	def add_wallet(self, wallet_id, passphrase, mnemonic, balance):
		return self.wallets.insert_one({"_id": wallet_id, "passphrase": passphrase, "mnemonic": mnemonic, "balance": balance})

	def delete_wallet(self, wallet_id):
		return self.wallets.delete_one({"_id": wallet_id})

	def get_wallets(self):
		res = []

		for i in self.wallets.find():
			res.append(i)

		return res

	def update_wallet(self, wallet_id, balance):
		return self.wallets.update_one({"_id": wallet_id}, {"$set": {"balance": balance}})


def main():
	os.system("clear")

	print("Введите адрес кошелька")
	address = input("> ")
	print()
	print("Введите количество монет ADA")
	amount = input("> ")

	os.system("clear")

	print(f"Вывод на кошелек: {address}")
	print(f"Количество монет ADA: {amount}")
	print()

	try:
		print(Fore.BLUE + "Получение адресов отправителя")
		itter = 1

		a = time.time()

		for wallet in mongo_tools.get_wallets():
			print(Fore.BLUE + f"Вывод с кошелька #{itter}")
			cardano_tools.create_transaction(wallet["_id"], address, amount, wallet["passphrase"])
			itter += 1

		b = time.time()

		print(Fore.GREEN + f"Все транзакции выполнены за {round(b-a, 1)} секунды")

	except Exception as ex:
		print(Fore.RED + f"Ошибка во время выполнения: {ex}")

	finally:
		print(Fore.BLUE + "Обновление базы данных")

		try:
			for wallet in mongo_tools.get_wallets():
				mongo_tools.update_wallet(wallet["_id"], cardano_tools.get_wallet(wallet["_id"]))

		except Exception as ex:
			print(Fore.RED + f"Ошибка во время обновления базы данных: {ex}")

		print()
		print(Fore.BLUE + "Нажмите любую клавишу, чтобы продолжить...")
		os.system("pause > NUL")	
		main()


if __name__ == '__main__':
	init(autoreset=True)
	cardano_tools = CardanoTools()
	mongo_tools = MongoTools()
	main()

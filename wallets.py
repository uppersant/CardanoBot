from cardano.backends.walletrest import WalletREST
from cardano.wallet import WalletService, Wallet
from random_word import RandomWords
from colorama import init, Fore
from mnemonic import Mnemonic
import pymongo
import random
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
	print()
	enter = input("> ")

	if enter.lower() == "add":
		try:
			wallet = cardano_tools.create_wallet()
			mongo_tools.add_wallet(wallet, wallet, wallet, wallet)
			print(Fore.GREEN + f"Новый кошелек создан и добавлен в БД: {wallet}")

		except Exception as ex:
			print(Fore.RED + f"Ошибка во время создания кошелька: {ex}")

		finally:
			main()
		

	elif enter.split(" ")[0].lower() == "delete":
		try:
			mongo_tools.delete_wallet(enter.split(" ")[1])
			print(Fore.GREEN + "Кошелек удален")

		except Exception as ex:
			print(Fore.RED + f"Ошибка во время удаления кошелька: {ex}")

		finally:
			main()

	elif enter.lower() == "update":
		try:
			for wallet in mongo_tools.get_wallets():
				mongo_tools.update_wallet(wallet["_id"], cardano_tools.get_wallet(wallet["_id"]))

			print(Fore.GREEN + "База данных обновлена")

		except Exception as ex:
			print(Fore.RED + f"Ошибка во время обновления базы данных: {ex}")

		finally:
			main()

	else:
		print(Fore.RED + "Неизвестная команда")
		main()


if __name__ == "__main__":
	os.system("clear")
	print("add - создает новый кошелек и добавляет в базу данных")
	print("delete + адрес кошелька - удаляет заданый кошелек")
	print("update - обновляет балансы кошельков в базе данных")
	init(autoreset=True)
	cardano_tools = CardanoTools()
	mongo_tools = MongoTools()
	main()

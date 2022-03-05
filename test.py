import pypubit

access = "DG5thHnveYstkVpxYzVUTeNKCbiwxiLkkoyaI7De"
secret = "oJVASua4brJxyvqr0NeQyYwO19x5UWNzUMOZGRV2"
upbit = pyupbit.Upbit(access, secret)
print(upbit.get_balance("KRW-BTC"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회
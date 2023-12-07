
class Trade:
    def __init__(self,my_uid : int,trader_uid : int,my_cards : [str],trader_cards: [str]) -> None:
        self.my_uid = my_uid
        self.trader_uid = trader_uid
        self.my_cards = my_cards
        self.trader_cards = trader_cards

    def get_trade_info(self , my_name, trader_name):
        r = f'**me ({my_name})** \n'
        for card in self.my_cards:
            r += f'\t{card}\n'
        r += f'\n **{trader_name}** \n '
        for card in self.trader_cards:
            r += f'\t{card}\n'
        return r

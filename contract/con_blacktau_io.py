import currency

balances = Hash(default_value=0)
symbol = Variable()
operator = Variable()

@construct
def seed(vk: str):
    balances[vk] = 1000000000
    balances["chips_value"] = 5
    balances["fees"] = 0.03
    symbol.set('GIFI')
    operator.set(vk)


@export
def buy_chips(amount: float):
    account = ctx.caller
    pool = operator.get()
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[pool] >= amount * balances["chips_value"], 'Not enough coins to send!'

    currency.transfer_from(amount, pool, account)

    balances[pool] -= amount * balances["chips_value"]
    balances[account] += amount * balances["chips_value"]
    balances[account, 'chips_count'] += (amount * balances["chips_value"])
    
@export
def set_winner_hand(amount:float, account: str, blackjack: bool):
    assert_owner()

    assert amount > 0, 'Cannot send negative balances!'
    pool = operator.get()
    account = account
    assert balances[pool] >= amount, 'Not enough coins to send!'

    balances[pool] -= amount
    balances[account] += amount  
    
    balances[account, 'chips_count'] += amount

    if blackjack is True:
        balances[account, 'blackjack_hands'] += 1 
        
    balances[account, 'winner_hands'] += 1

    if balances[account, 'plays_count'] is not None:
        winratio = ((balances[account, 'winner_hands'] * 100) / balances[account,'plays_count']) 
        if winratio > 100:
            winratio = 100
    else:
        winratio = '0%'

    winratio = "{:.2f}".format(winratio)
    balances[account, 'win_ratio'] = str(winratio) + '%'

@export
def tie_hand(amount:float, account: str):
    assert_owner()
    assert amount > 0, 'Cannot send negative balances!'
    pool = operator.get()
    assert balances[pool] >= amount, 'Not enough coins to send!'

    balances[pool] -= amount
    balances[account] += amount  

    balances[account, 'chips_count'] += amount

 
@export
def set_loser_hand(account: str):
    assert_owner()

    if balances[account, 'plays_count'] is not None:
        winratio = ((balances[account, 'winner_hands'] * 100) / balances[account,'plays_count']) 
        if winratio > 100:
            winratio = 100
    else:
        winratio = '0%'

    winratio = "{:.2f}".format(winratio)
    balances[account, 'win_ratio'] = str(winratio) + '%'

@export
def bet(amount: float, account: str):
    assert_owner()  
    assert amount > 0, 'Cannot send negative balances!'    
    pool = operator.get()   
    assert balances[account] >= amount, 'Not enough coins to send!'
    balances[account] -= amount
    balances[pool] += amount
    balances[account, 'plays_count'] += 1    
    balances[account, 'chips_count'] -= amount



@export
def bet_self(amount: float):
    assert amount > 0, 'Cannot send negative balances!'
    sender = ctx.caller
    pool = operator.get()
    assert balances[sender] >= amount, 'Not enough coins to send!'

    balances[sender] -= amount
    balances[pool] += amount
    balances[sender, 'plays_count'] += 1    
    balances[sender, 'chips_count'] -= amount

    
@export
def pay(amount: float, account: str):
    assert_owner()
    assert amount > 0, 'Cannot send negative balances!'
    sender = operator.get()
    assert balances[account] >= amount, 'Not enough coins to send!'
  
    total_balance = amount / balances["chips_value"]
    total_balance -= (total_balance * balances["fees"])

    currency.transfer_from(total_balance, account, sender)

    balances[account] -= amount   
    balances[account, 'chips_count'] -= amount
    balances[sender] += amount


@export
def pay_self(porcent: float):
    assert porcent > 0, 'Cannot send negative balances!'
    account = ctx.caller
    sender = operator.get()

    amount = balances[account] * (porcent/100)
    
    assert balances[account] >= amount, 'Not enough coins to send!'
  
    total_balance = amount / balances["chips_value"]
    total_balance -= (total_balance * balances["fees"])
    currency.transfer_from(total_balance, account, sender)

    balances[account] -= amount
    balances[account, 'chips_count'] -= amount
    balances[sender] += amount

@export
def transfer(amount: float, to: str):
    assert_owner()
    assert amount > 0, 'Cannot send negative balances!'
    sender = ctx.caller
    assert balances[sender] >= amount, 'Not enough coins to send!'

    balances[sender] -= amount
    
    balances[sender, 'chips_count'] -= amount

    balances[to] += amount
    balances[to, 'chips_count'] += amount



@export
def balance_of(account: str):
    return balances[account]

@export
def allowance(owner: str, spender: str):
    return balances[owner, spender]

@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller
    balances[sender, to] += amount
    return balances[sender, to]

@export
def change_value(value: float):
    assert_owner()
    assert value > 0, 'Cannot send negative value!'

    balances["chips_value"] = value

@export
def change_fees(value: float):
    assert_owner()
    balances["fees"] = value


def assert_owner():
    assert ctx.caller == operator.get(), 'Only operator can call!'

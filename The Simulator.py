
#  Libraries
from SimPy.Simulation import *
from random import randint
import numpy as np
import math
import csv
import matplotlib.pyplot as con0
import matplotlib.pyplot as All_Pro
import matplotlib.pyplot as C_H
import matplotlib.pyplot as C_C


# This part for cost calculation ( smart contract invocation )
GUR = 204739  # Gas used for registration
GUS = 620865  # Gas used for setup
GUA = 144367  # Gas used for Authentication (sending the receipt)
GP = 4.2  # Gas Price
# ------------------------------------------------------------------
unreportedRequest = 0
NewConReject = 0

Trades = []
waitingTime = []
MsgSent = 0
TradeSpace = 2000
ParticipantSpace = 10


# This variables for the con0 plotting
con0Trade = []
con0Rep = []
pr0Trade = []
pr0Rep = []

## Class Declaration (User Defined) ------------
class Participant:
    id = 0
    TradeInvolved = 0
    TotalGotMsg = None
    TotalTradeMsg = None
    RawRep = 0
    score = 0
    Reject = 0
    NewConReject = 0
    UnReTr = 0
    chance = 0
    group = 'f'
    TC = 0
    AC = 0
    Stops = 0
    ReceiptNo = 0
    WillBehave = None
    In = 0
    WillStop = None
    WillStopIn = 0



class ParticipantPro:
    id = 0
    TradeInvolved = 0
    TotalGotMsg = None
    TotalTradeMsg = None
    RawRep = 0
    score = 100
    Reject = 0
    NewConReject = 0
    UnReTr = 0
    chance = 0
    group = 'f'
    TC = 0
    AC = 0
    Stops = 0
    WillStop = None
    WillStopIn = 0


class TradeInformation:
    id = int
    pro = Participant
    con = Participant
    TA = []
    status = bool
    BN = int  # batch number ( the amount of batches )
    ReceiptN = int
    MsgN = int  # the number of msg deleviered
    payment = int  # paid by consumer to the msg delevired
    total = int  # total payment suppose to be for the trade specification in TA
    TimeTaken = float


# General Declaration ---------------------------
Producers = [ParticipantPro() for each in range(ParticipantSpace)]
Consumers = [Participant() for each in range(ParticipantSpace)]

TradeInfo = [TradeInformation]

ConRepPlot = [list() for each in range(ParticipantSpace)]
ConTrade = [list() for each in range(ParticipantSpace)]
ProRepPlot = [list() for each in range(ParticipantSpace)]
ProTrade = [list() for each in range(ParticipantSpace)]

ProH = []
ProC = []
ConH = []
ConC = []

BT = 4.0  # round(random.uniform(1.00, 5.00),2) # random value for batch sending time --> used by producer (Batch Sending time)
BRT = 2.0  # --> used by consumer (Batch Receiving Time)
RT = randint(1, 5)  # --> used by consumer (Receipt Sending Time) (It is random because it is based on GP
RRT = 2.0  # --> used by smart contract (Receipt Receiving Time)
ACK = 2.0  # --> used by smart contract (Acknowlege by smart contract)
SMPT = 3.0  # --> used by smart contract ( Smart Contract Process Time ) to compare the receipt with the batch size

Times = {'BT': BT, 'BRT': BRT, 'RT': RT, 'RRT': RRT, 'SMPT': SMPT, 'ACK': ACK}

ConWaitingTime = [0.00]
payment = 0.00
MaxTime = 100000.0  # the max time of the simulation

tempTrade = TradeInformation
# -----------------------------------------
BatchStatus = 'not'

def Batchsent():
    return BatchStatus == 'sent'

def BatchChange():
    global BatchStatus
    BatchStatus = 'not'


# -----------------------------------------
ReceiptStatus = 'not'

def Receiptsent():
    return ReceiptStatus == 'sent'

def ReceiptChange():
    global ReceiptStatus
    ReceiptStatus = 'not'


# -----------------------------------------
ACKStatus = 'not'

def ACKsent():
    return ACKStatus == 'sent'

def ACKchange():
    global ACKStatus
    ACKStatus = 'not'


# -----------------------------------------
BatchNumber = 0

def BatchNumberUpdate(NewValue):
    global BatchNumber
    BatchNumber += NewValue

def BatchNumberReset():
    global BatchNumber
    BatchNumber = 0


# -----------------------------------------

MsgDelivered = 0

def MsgDeliveredUpdate(NewValue):
    global MsgDelivered
    MsgDelivered += NewValue

def MsgDeliveredReset():
    global MsgDelivered
    MsgDelivered = 0

# ------------------------------------------
ReceiptDelivered = 0

def ReceiptDeliveredUpdate(NewValue):
    global ReceiptDelivered
    ReceiptDelivered += NewValue

def ReceiptDeliveredReset():
    global ReceiptDelivered
    ReceiptDelivered = 0

# ---------------------------------------------

NewConReq = 0

def NewConReqUpdate(value):
    global NewConReq
    NewConReq = value

def NewConReqReset():
    global NewConReq
    NewConReq = 0


# -------------------------------------------

Response = 0

def ResponseUpdate(value):
    global Response
    Response = value

def ResponseReset():
    global Response
    Response = 0

# -------------------------------------------

timeout = 0

def timeoutUpdate(value):
    global timeout
    timeout = value

def timeoutReset():
    global timeout
    timeout = 0

# --------------------------------------------

CS = 0

def CSUpdate():
    global CS
    CS = 1

def CSReset():
    global CS
    CS = 0

# -------------------------------------------
PS = 0

def PSUpdate():
    global PS
    PS = 1

def PSReset():
    global PS
    PS = 0

# ---------------------------------------------

TS = -1

def TSUpdate(value):  # trade state
    global TS
    TS = value

def TSReset():
    global TS
    TS = -1

# ---------------------------------------------
# The variables of LP part:
LP = 0
LPN = 0
LPFlag = False
TimeRemain = 0

def LPReset():
    global LP
    global LPN
    global LPFlag
    LP = 0
    LPN = 0
    LPFlag = False
    global TimeRemain
    TimeRemain = 0


## Simulation Process Declaration-------------------------------------

class Marketplace(Process):
    def general(self, pro_num, con_num, TA, Times, mon):

        p = Producer(name="Producer%02d" % (pro_num))
        c = Consumer(name="Consumer%02d" % (con_num))
        sm = SmartContract(name="SmartContract")

        # update the BT value based on the BS
        Times['BT'] = TA['BS'] / TA['rate']

        activate(p, p.sendBatch(TA, Times['BT'], mon), at=TA['from'])  # start send batch
        yield hold, self, (0.5 + TA['from'])

        activate(c, c.sendReceipt(TA, Times['BRT'], Times['RT']))
        yield hold, self, 0.5

        activate(sm, sm.notify(Times, mon, con_num))
        yield hold, self, 0.5

        yield waituntil, self, ACKsent
        yield hold, self, 2.0  # Juts to give the producer time to passivate


        BatchChange()
        ReceiptChange()
        ACKchange()

        while (round(now(), 2) < TA['to']):

            print' the time now is ', round(now(), 2)

            if ((TA['to'] - round(now(), 2)) < Times['BT']):  # BT =TA['BS']/TA['Rate']
                LPFlag = True


            print' the time now is **', round(now(), 2)

            reactivate(p)  # start send batch

            yield hold, self, 0.5

            reactivate(c)
            yield hold, self, 0.5

            reactivate(sm)
            yield hold, self, 0.5

            yield waituntil, self, ACKsent

            yield hold, self, 0.2  # just to give the producer the time to finish its work

            BatchChange()
            ReceiptChange()
            ACKchange()

        print ('the time now before end GENERAL process is %7.2f' % (round((now() - 0.2), 2)))

        mon[0].observe(BatchNumber)
        totalTime = round((now() - 0.2), 2)
        mon[1].observe(totalTime)
        mon[2].observe(MsgDelivered)
        mon[3].observe(ReceiptDelivered)
        mon[4].observe(LP)
        stopSimulation()

class Producer(Process):

    def sendBatch(self, TA, BT, mon):

        while True:
            print ('%7.4f: (%s) I am Here' % (now(), self.name))

            # Part 1: send the batch to the consumer
            global BatchStatus
            global LPFlag

            yield hold, self, BT

            print('%7.4f:  %s -- Sent Batch' % (now(), self.name))

            BatchStatus = 'sent'

            if (LPFlag == False):
                BatchNumberUpdate(1)
                print (' new batch recorded')

            # Part 2: Receive the ACK from the smart contract

            if ACKsent():
                msg = 'ACK received '
            else:
                msg = 'wait for the ACK'

            print ('%7.4f: %s -- ' % (now(), self.name))
            print (msg)

            yield waituntil, self, ACKsent

            print (' %7.4f: %s -- ACK Received ' % (now(), self.name))

            yield passivate, self


class Consumer(Process):

    def sendReceipt(self, TA, BRT, RT):
        while True:
            # Part 1: Receive the Batch from the producer
            print ('%7.4f: (%s) I am Here' % (now(), self.name))

            yield waituntil, self, Batchsent
            print('%7.4f: %s -- Batch Received from the producer and it is the time to' % (now(), self.name))
            # ------------------------------------------------------------------------

            # Part 2: Send the Receipt to the smart contract
            print('send the receipt to the smart contract: ')

            global ReceiptStatus

            yield hold, self, RT

            print ('%7.4f:  %s -- Sent Receipt' % (now(), self.name))

            ReceiptStatus = 'sent'

            yield passivate, self

class SmartContract(Process):

    def notify(self, Times, mon, con_num):
        # Part 1: Receive the Receipt from the consumer

        while True:

            print ('%7.4f: (%s) I am Here' % (now(), self.name))

            yield waituntil, self, Receiptsent
            print ('%7.4f: %s -- Receipt Received from the consumer' % (now(), self.name))
            # Now, the smart contract will compare the receipts with the actual number of messages deleivered in the batch)

            """Based on consumer reputation (honesty): 

                        The options are either : 
                        1- consumer not send receipt represented by -1
                        2- consumer send wrong number of msg comparing with BS from (0 to BS-1)
                        3- consumer send correct receipt = BS 
                        Probability = reputation honest(opt3) + {opt1 + opt2} """

            # -------------------------------------------------------------- Receipt Prob
            # This probability for receiving a receipt or not or correct number of receipts

            x = randint(-1, (int(TA['BS']) - 1))  # from -1 (not send) to BS-1 (sending wrong msg amount in the BS)

            if (ConsumerFreChange == True or Consumers[Con_num].WillBehave == 'h'):

                Receipt = TA['BS']

            elif (Consumers[Con_num].WillBehave == 'c'):

                if (((ReceiptDelivered + 1) == Consumers[Con_num].In)):

                    Receipt = x

                else:
                    Receipt = TA['BS']

            print ' the receipt is ', Receipt
            print ' and the BS is ', TA['BS']

            # ------------------------------------------------------- CondecideToStop Prob
            # This probability is for consumer to stop the trade
            # stop the trade --- the choice (1)
            # continue the trade -- choice (0)

            if (ConsumerFreChange == True or Consumers[Con_num].WillStop == 'n'):

                CondecideToStop = 0

            elif (Consumers[Con_num].WillStop == 'y'):

                if (((ReceiptDelivered + 1) == Consumers[Con_num].WillStopIn)):
                    CondecideToStop = 1
                else:
                    CondecideToStop = 0

            print ' the value of ConDecideToStop is :', CondecideToStop

            # ---------------------------------------------------------------------------- ProDeceideToStop Pro

            # Here Adding the part of Producer stop or not --------------

            ProdecideToStop = 0  # was -10

            if (ProducerFreChange == True or Producers[Pro_num].WillStop == 'n'
                    or Producers[Pro_num].group == 'h'):

                ProdecideToStop = 0

            elif (Producers[Pro_num].WillStop == 'y'):

                if (((ReceiptDelivered + 1) == Producers[Pro_num].WillStopIn)):

                    ProdecideToStop = 1
                else:
                    ProdecideToStop = 0

            print ' The value of ProDecideToStop is ', ProdecideToStop

            if (Receipt != -1):  # SEND a receipt either full or not
                # if (Receipt == TA['BS']): # This if is the correct one. because only a consumer can
                # stop if and only if the trade is success ( otherwise, it will be terminated immediately by SC)

                # This part if consumer send receipt
                # we have to set a probability if he would stop the trade or not

                # ----------------------------------------------- Receipt Recording-------------------------------
                MsgDeliveredUpdate(Receipt)
                ReceiptDeliveredUpdate(1)
                print (' new update for the total receipt by ')
                print (Receipt)

                if (Receipt != TA['BS']):

                    # (will stop automatically)

                    if (LPFlag == False):


                        print '%7.4f: The Receipt!= BS, Should terminate , the receipt is' % now()
                        print(Receipt)
                        print('terminate')

                        BatchChange()
                        ReceiptChange()
                        ACKchange()

                        mon[0].observe(BatchNumber)
                        mon[1].observe(round(now(), 2))
                        mon[2].observe(MsgDelivered)
                        mon[3].observe((ReceiptDelivered))
                        stopSimulation()
                        break

                    elif (LPFlag == True):
                        print('It is LP')
                        LP = Receipt
                        ReceiptDeliveredUpdate(1)  # the receipt of the LP
                        LPN = 1

                if (ProdecideToStop or CondecideToStop):

                    if (ProdecideToStop):
                        print'producer decides to stop '
                        Producers[Pro_num].Stops += 1
                        PSUpdate()

                    if (CondecideToStop):
                        print' consumer decides to stop '
                        Consumers[Con_num].Stops += 1
                        CSUpdate()

                    BatchChange()
                    ReceiptChange()
                    ACKchange()

                    mon[0].observe(BatchNumber)
                    mon[1].observe(round(now(), 2))
                    mon[2].observe(MsgDelivered)
                    mon[3].observe((ReceiptDelivered))
                    stopSimulation()
                    break


            elif (Receipt == -1):  # don't send a receipt
                print('The consumer does not send the receipt')
                print('terminate')
                BatchChange()
                ReceiptChange()
                ACKchange()

                mon[0].observe(BatchNumber)
                mon[1].observe(round(now(), 2))
                mon[2].observe(MsgDelivered)
                mon[3].observe((ReceiptDelivered))
                stopSimulation()
                break

            # ------------------------------------------------------------------------

            # Part 2: Send the ACK to the producer
            print ('%7.4f: %s -- Send the ACK to the producer (to all network): ' % (now(), self.name))

            global ACKStatus

            yield hold, self, ACK

            print ('%7.4f: %s -- ACK sent' % (now(), self.name))

            ACKStatus = 'sent'

            yield passivate, self


## Method declarations---------------------------------------------
def TAGenerator(rep):
    # Here we have to set a random number for the timeout respond time and
    # set a probability for producer response

    # timeoutValue = round (random.uniform(2.00,100.0),2)

    # assign values to TA
    x1 = round(random.uniform(1000.00, 5000.00), 2)  # random value to start
    x2 = round(random.uniform(1000.00, 5000.00), 2)  # random value to end
    startTime = 0.0  # startTime  = min(x1,x2) -- always start from zero to avoid delay in simulation if start from x (just for accelrating the simulation )
    endTime = max(x1, x2)
    rate = 100  # 100 msg per second
    TATI = endTime - startTime
    ETM = rate * TATI

    price = round(random.uniform(1.00, 50.00), 2)  # the price in USD ( and here is just as an example)


    # This part is for set the BS ( it is a function of consumer reputation)
    timetakeforSend = 0.2  # time taken for every unit to be sent
    totalMsgSend = math.ceil((endTime - startTime) / timetakeforSend)  # total messages could be sent through TA window

    # print 'the total msg sent is '
    # print totalMsgSend
    print 'the consumer repu is', rep
    global BS
    # This part assigns the value of the BS based on consumer reputation {BS=f(c.reputation)}
    if (rep > 0.00 and rep <= 100.00):
        # global BS # To solve the problem UnboundLocalError: local variable 'BS' referenced before assignment

        print ' TATI is ', TATI

        print ' ETM is ', ETM

        print ' the formula is', math.log(rep / 100.00 + 1) / 2.77
        # BS = rate * rep
        moni = rep / 100.00

        print 'moni is ', moni
        BS = math.log(moni + 1) / 2.77 * ETM
        print (' BS1 ')
        print(BS)

    elif (rep == 0.00):
        # global BS # To solve the problem UnboundLocalError: local variable 'BS' referenced before assignment
        BS = 10  # just an example
        print ('BS2 ')
        print (BS)


    print ('The value of BS inside the method is: ')
    print (BS)

    EBN = int(TATI / ((BS / rate) + RT))

    print ' the estimated Batch number EBN  is ', EBN

    TA = {'from': startTime, 'to': endTime, 'rate': rate, 'BS': BS, 'price': price, 'TATI': TATI, 'EBN': EBN}

    return TA


def start(i, j, TA, Times):
    wM = [Monitor(), Monitor(), Monitor(), Monitor(), Monitor()]
    """
    1 for number of batches from(p) 
    2 total time (Whole Trade)  
    3 total number of msg delivered from (c) - count (number of receipts received) , total ( number of msg delivered)
    4 total number of LP if exists 
    """

    initialize()

    mk = Marketplace(name="MK")
    activate(mk, mk.general(i, j, TA, Times, mon=wM))

    simulate(until=MaxTime)

    return (wM[0].total(), wM[1].total(), wM[2].total(), wM[3].total(), wM[4].total())  # ,wM[2].count()

    """
    wM[0].count() to count how many batches sent by producer 
    wM[1].total() to return the total time taken for the trade to be done - used to check the trade status 
    wM[2].total() to count how many messgaes delivered by consumer 
    wM[2].count() to count the total number of receipts delivered
    wM[4].total() to return the total number of LP if exists
    """


print('------- The simulation start -----')

# Add the ( intent Probability ) for both producers and consumers
# Which means distribute the participants randomaly into two group, honest and cheater

# # For Producers
for counter in range(ParticipantSpace):
    choice = np.random.choice((0, 1), p=[0.5, 0.5])
    if (choice):
        Producers[counter].group = 'h'
    else:
        Producers[counter].group = 'c'


Producers[0].group = 'h'

# For Consumers
for counter in range(ParticipantSpace):
    choice = np.random.choice((0, 1), p=[0.5, 0.5])
    if (choice):
        Consumers[counter].group = 'h'
    else:
        Consumers[counter].group = 'c'

# Add this here to add the trade 1 in the plot
for k in range(ParticipantSpace):
    ConRepPlot[k].append(Consumers[k].score)
    ConTrade[k].append(Consumers[k].TradeInvolved)
    ProRepPlot[k].append(Producers[k].score)
    ProTrade[k].append(Producers[k].TradeInvolved)

# con0Rep.append(Consumers[0].score)
# con0Trade.append(Consumers[0].TradeInvolved)
#
# pr0Rep.append(Producers[0].score)
# pr0Trade.append(Producers[0].TradeInvolved)

# ranFre = 0
set = 1
ranFre = randint(5, 20)
comp = ranFre

for i in range(1, TradeSpace + 1):  # we have 50 trades between random producer and consumer each trade
    # ConWaitingTime = [] #update the waiting time value for each trade

    # choose a producer and consumer randomly
    Pro_num = randint(0, 9)
    # Pro_num = 0
    Con_num = randint(0, 9)
    # Pro_num = 0
    # Con_num = 0

    Producers[Pro_num].id = Pro_num
    Consumers[Con_num].id = Con_num

    #  ----------------------------------Honest or Cheat ----------------------
        # here will decide if the consumer will cheat or be honest in this trade
        # ( at the begining of the trade)

        ConRep = Consumers[Con_num].score / 100.00
        rest = 1 - ConRep

        Consumers[Con_num].WillBehave = np.random.choice(('h', 'c'), p=[ConRep, rest])

        if ( Consumers[Con_num].WillBehave == 'c'):
            Consumers[Con_num].In = randint(1,TA['EBN']) # choose which receipt he will cheat in

        elif (Consumers[Con_num].WillBehave == 'h'):
            Consumers[Con_num].In = -1

    #  --------------------------------Stop or not


    print(' the value of batchstatus is ')
    print (BatchStatus)

    print(' the value of receiptStatus is ')
    print (ReceiptStatus)

    print(' the value of ACKStatus is ')
    print (ACKStatus)

    print(' Trade %02d' % i)
    print (' *****  Simulation between producer%02d and consumer%02d *****' % (Pro_num, Con_num))

    # -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
    ProducerFreChange = False
    ConsumerFreChange = False

    # Add a random number here to choose a trade which either producer or consumer
    # behave well to create some fluctuation in trades plots
    # The idea: while everything in this code is based on the participant reputation,
    # this means the low reputation always getting down while we in (real case) sometimes need to behave good
    # to see how the marketplace is doing
    # Let say every 50 trades choose one random number x and then every x  in trades 1-50
    # assign a high reputation for either one participant or both.
    # Then in the next period 51-100 choose another number and change the pattern

    print ' the ranFre is ', ranFre

    if (i == comp and i < (set * 50)):

        print ' entering here'

        # if ( i == (base + ranFre) and (base + ranFre) <= (set * 50)):

        # Here we pretent that an honest behaviour is done by producer and conusmer
        # or one of them
        # who = randint(1, 1) # just test 16 Sep
        who = randint(1, 2)  # just test 16 Sep
        # who = randint(1, 1)  # test again in 24 Sep
        # 1 --> producer
        # 2 --> consumer

        print ' who is ', who

        if (who == 1):
            ProducerFreChange = True
            temp = Pro_num
            print ' In trade: %2d the ProducerFreChange is true ' % i

        elif (who == 2):
            ConsumerFreChange = True
            temp = Con_num
            print ' In trade: %2d the ConsumerFreChange is true ' % i

        # ProducerFreChange = True
        # ConsumerFreChange = True

        # Recording the fluctuation of trades and who is the honest
        with open('fluctuationConRun.csv', 'a') as t_file:
            writer = csv.writer(t_file)
            writer.writerow([ranFre, i, who, temp])

        temp = -1

        comp += ranFre
        print ' the next comparision in trade ', comp

    if (i == set * 50):
        print ' we are in the second if '
        set += 1
        ranFre = randint(5, 20)
        comp = i + ranFre

        print " The new value of ranFre is ", ranFre
        print ' the new value of comp is ', comp


    # -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

    # HERE Producer can reject the trade request from new consumer

    # here add a probability for a consumer and producer to pay the fees to make his negative reputation to 0

    # This pro for producer
    # if (Producers[Pro_num].score < 0 and Producers[Pro_num].chance < 2):
    #
    #     decideToPay = np.random.choice((0, 1), p=[0.5, 0.5])
    #
    #     if (decideToPay):
    #         Producers[Pro_num].chance += 1
    #         while (Producers[Pro_num].score < 0):
    #             Producers[Pro_num].RawRep += 1
    #             Producers[Pro_num].score = Producers[Pro_num].RawRep / Producers[Pro_num].TradeInvolved

    # This pro for Consumer tp Pay
    if (Consumers[Con_num].score < 0 and Consumers[Con_num].chance < 2):

        decideToPay = np.random.choice((0, 1), p=[0.5, 0.5])

        if (decideToPay):
            Consumers[Con_num].chance += 1
            while (Consumers[Con_num].score < 0):
                Consumers[Con_num].RawRep += 1
                Consumers[Con_num].score = Consumers[Con_num].RawRep / Consumers[Con_num].TradeInvolved
            print " the consumer %2d has decided to pay and now his reputation is : " % Con_num, Consumers[
                Con_num].score

    if (Consumers[Con_num].score >= 0 and Producers[Pro_num].score >= 0):

        print " the old ( before start this trade yet) Producers[%2d].score is " % Pro_num, Producers[Pro_num].score
        print " the old ( before start this trade yet) Consumer[%2d].score is  " % Con_num, Consumers[Con_num].score

        ProRep = Producers[Pro_num].score / 100.00

        print 'ProRep is ', ProRep

        # ----------------------------------------------------------------------------Accepting/Rejecting new request Prob
        # This propability for a producer to accept or reject new request

        # accept -- choice (1)
        # reject -- choice (0)

        rest = 1.00 - ProRep

        print ' rest is ', rest

        # bigger = max(rest, ProRep)
        # smaller = min(rest, ProRep)

        if (ProducerFreChange == True or Producers[Pro_num].group == 'h'):

            ProChoice = 1  # This part if for the fluctuation section ( means will accept the trade)

        elif (ProRep == 1.00 and Producers[Pro_num].group == 'h' and Producers[Pro_num].TradeInvolved == 0):

            ProChoice = np.random.choice((0, 1), p=[0.2, 0.8])

        elif (ProRep == 1.00 and Producers[Pro_num].group == 'c' and Producers[Pro_num].TradeInvolved == 0):

            ProChoice = np.random.choice((0, 1), p=[0.8, 0.2])

        # elif (ProRep == 1.00): # represent the highest repu could have
        #
        #     theTotal = Producers[Pro_num].Stops + Producers[Pro_num].UnReTr + Producers[Pro_num].Reject + Producers[Pro_num].TradeInvolved
        #
        #
        #     if ( theTotal == 0):
        #         willReject = 0
        #     else:
        #
        #         willReject = Producers[Pro_num].Reject / theTotal
        #     WillAccept = 1 - willReject
        #
        #     print ' the part of accept or reject new request:'
        #     print 'WillReject is ', willReject
        #     print ' WillAccept is ', WillAccept
        #
        #     # ProChoice = np.random.choice((0, 1), p=[0.5, 0.5])
        #     ProChoice = np.random.choice((0, 1), p=[willReject, WillAccept])
        else:
            # This line for this else
            # ProChoice = np.random.choice((0, 1), p=[rest, ProRep])  # This prob will be based on producer reputation

            # ------------------ 24 Sep ----- This part is for elif above -------------
            theTotal = Producers[Pro_num].Stops + Producers[Pro_num].UnReTr + Producers[Pro_num].Reject + Producers[
                Pro_num].TradeInvolved

            if (theTotal == 0):
                willReject = 0
            else:
                willReject = Producers[Pro_num].Reject / theTotal
            WillAccept = 1 - willReject

            print ' the part of accept or reject new request:'
            print 'WillReject is ', willReject
            print ' WillAccept is ', WillAccept

            # ProChoice = np.random.choice((0, 1), p=[0.5, 0.5])
            ProChoice = np.random.choice((0, 1), p=[willReject, WillAccept])

            # ------------------ 24 Sep ----- END This part is for elif above -------------

        # # This part has been added in 17 Oct ( to evaluate fixing the producer)
        # ProChoice = 1 # means decide to accept all trades ever
        # # The end of: This part has been added in 17 Oct ( to evaluate fixing the producer)

        # I have put this part here to cancel or continue the trade ( as request queue)
        timeoutUpdate(randint(2, 100))

        ProRep = Producers[Pro_num].score / 100.00

        # This probability for a producer for unreport for requests
        rest = 1.00 - ProRep
        minRes = 1
        maxRes = int(timeout * 80 / 100)
        x = randint(minRes, maxRes)  # from -1 (not send) to BS-1 (sending wrong msg amount in the BS)
        # x = randint(1, timeout/2) # let all reposnd half time at max to reduce the Res value
        # # just test 16 sep

        # -------------------------------------------------------------------------- Response Prob

        if (ProducerFreChange == True or Producers[
            Pro_num].group == 'h'):  # This is for the fluctuation section (will respond to the request as quick as possible)

            ResponseUpdate(0)  # This is the best value could be, which is a response at the time of asking the request

        elif (ProRep == 1.00 and Producers[Pro_num].group == 'h' and Producers[Pro_num].TradeInvolved == 0):

            ResponseUpdate(np.random.choice((x, timeout + 1), p=[0.8, 0.2]))

        elif (ProRep == 1.00 and Producers[Pro_num].group == 'c' and Producers[Pro_num].TradeInvolved == 0):

            ResponseUpdate(np.random.choice((x, timeout + 1), p=[0.2, 0.8]))

        # elif (ProRep == 1.00):
        #
        #     theTotal = Producers[Pro_num].Stops + Producers[Pro_num].UnReTr + Producers[Pro_num].Reject + Producers[Pro_num].TradeInvolved
        #
        #     if ( theTotal == 0):
        #         willNotRespond = 0
        #     else:
        #
        #         willNotRespond = Producers[Pro_num].UnReTr / theTotal
        #
        #     WillRespond = 1 - willNotRespond
        #     #
        #     #
        #
        #     print ' the part of unreport for requests:'
        #     print ' the willNotRespond is :', willNotRespond
        #     print ' the WillRespond is:', WillRespond
        #
        #     # ResponseUpdate(np.random.choice((x, timeout + 1), p=[WillRespond, willNotRespond]))
        #     ResponseUpdate(np.random.choice((x, timeout + 1), p=[0.5, 0.5]))
        else:

            # This line is for this else -- has been changed in 24 Sep
            # ResponseUpdate(
            #     np.random.choice((x, timeout + 1), p=[ProRep, rest]))  # This prob will be based on consumer reputation

            # This part has been added in 24 Sep ------ the part of elif above
            theTotal = Producers[Pro_num].Stops + Producers[Pro_num].UnReTr + Producers[Pro_num].Reject + Producers[
                Pro_num].TradeInvolved

            if (theTotal == 0):
                willNotRespond = 0
            else:

                willNotRespond = Producers[Pro_num].UnReTr / theTotal

            WillRespond = 1 - willNotRespond
            #
            #

            print ' the part of unreport for requests:'
            print ' the willNotRespond is :', willNotRespond
            print ' the WillRespond is:', WillRespond

            # ResponseUpdate(np.random.choice((x, timeout + 1), p=[WillRespond, willNotRespond]))
            ResponseUpdate(np.random.choice((x, timeout + 1), p=[0.5, 0.5]))

            if (theTotal == 0):
                willNotRespond = 0
            else:

                willNotRespond = Producers[Pro_num].UnReTr / theTotal

            WillRespond = 1 - willNotRespond
            #
            #

            print ' the part of unreport for requests:'
            print ' the willNotRespond is :', willNotRespond
            print ' the WillRespond is:', WillRespond

            ResponseUpdate(np.random.choice((x, timeout + 1), p=[WillRespond, willNotRespond]))
            # ResponseUpdate(np.random.choice((x, timeout + 1), p=[0.5, 0.5]))

            # End of the part 24 Sep -------------------------------

        # # This part has been added in 17 Oct ( to evaluate fixing the producer )
        # ResponseUpdate(0) # The optimal time (from timeout) for producer to respond to the request ( no UR)
        # # The end of : This part has been added in 17 Oct ( to evaluate fixing the producer )

        # This line ONLY to solve the error " NameError: name 'flag' is not defined "
        flag = False
        UnReFlag = False

        # Section 1: Rejetc or Unreport the trade request

        # This is the new if ( 12 Sep )
        if ((ProChoice == 0) or (Response > timeout)):
            # that means he decides to reject the request -- 1 means accept the trade
            # Either reject or unreport  the trade request

            TSUpdate(0)

            Q = -1  # adding this to solve the error " is not defined" and also no value here
            # for Q because it is rejected/unreported

            # Reject the trade request
            if (ProChoice == 0):

                print " The producer has reject the trade request and should stop "
                Producers[Pro_num].Reject += 1

                print ' the Reject is for producer %2d' % Pro_num
                print ' is ', Producers[Pro_num].Reject

                if (Consumers[Con_num].score == 0):
                    Producers[Pro_num].NewConReject += 1
                    flag = True

                    print ' the Reject is for producer %2d for new consumer ' % Pro_num
                    print ' is ', Producers[Pro_num].NewConReject

            # Unreport the trade request
            elif (Response > timeout):

                print " The producer has ignored the request ( the request is unreported) .. "
                print ' you will be panushed for the unreported request'

                unreportedRequest = unreportedRequest + 1
                Producers[Pro_num].UnReTr = Producers[Pro_num].UnReTr + 1
                UnReFlag = True

                print ' the UR is for producer %2d' % Pro_num
                print ' is ', Producers[Pro_num].UnReTr

            # here we have to call the producer reputation method

            # Start the reputtaion calculation for only :
            # 1- reject new consumer 2- Unreport request
            if (UnReFlag or flag):

                print ' The producer TrV is :', Producers[Pro_num].TradeInvolved

                if (flag):  # reject for a new consumer

                    Res = 100 - (float(Response) / float(timeout) * 100.00)

                    if (flag and Producers[Pro_num].TradeInvolved == 0 and Producers[Pro_num].UnReTr == 0):
                        print " The flag is True for the first trade ever , means rejetc new consumer "
                        cur = (100 + Res) / 2
                    else:
                        print "The flag is True, means rejetc new consumer "
                        cur = Res

                elif (UnReFlag):

                    if (Producers[Pro_num].UnReTr == 1 and Producers[Pro_num].TradeInvolved == 0 and Producers[
                        Pro_num].NewConReject == 0):
                        print " The UnReFlag is True for the first time ever, means unreport request either new or old consumer "
                        cur = (100 + 0) / 2

                    else:
                        print " The UnReFlag is True, means unreport request either new or old consumer"
                        cur = 0

                print ' the curr after the section is :', cur

                # adding the current the the Rew ( Update Raw)
                Producers[Pro_num].RawRep += cur

                print ' the RawRep after adding the curr is :', Producers[Pro_num].RawRep

                # Producer Reputation Calculation

                print ' the values before the reputation calculation as the following:'
                print ' TrV is : ', Producers[Pro_num].TradeInvolved
                print ' UnRe is :', Producers[Pro_num].UnReTr
                print ' NewConReject is :', Producers[Pro_num].NewConReject

                Producers[Pro_num].score = round(Producers[Pro_num].RawRep / (
                        Producers[Pro_num].TradeInvolved + Producers[Pro_num].UnReTr + Producers[Pro_num].NewConReject),
                                                 2)

                print " the updated producer score is ", Producers[Pro_num].score

                Pun = -1  # this only to solve the error : NameError: name 'Pun' is not defined

                # This part has been added in 25 Sep
                ProRepPlot[Pro_num].append(Producers[Pro_num].score)
                ProTrade[Pro_num].append(i)
                # End of the part 25 Sep

                with open('ProRepRecordConRun.csv', 'a') as t_file:
                    writer = csv.writer(t_file)
                    writer.writerow([i,
                                     Pro_num, Producers[Pro_num].score,
                                     Con_num, Consumers[Con_num].score,

                                     '*', '*', '*',

                                     '*', '*', Pun, Q,

                                     Producers[Pro_num].UnReTr, Producers[Pro_num].Reject, Response, timeout,

                                     Producers[Pro_num].NewConReject,

                                     Producers[Pro_num].Stops, Producers[Pro_num].TradeInvolved,

                                     '*', '*', 'True', 'False',
                                     Producers[Pro_num].chance, Consumers[Con_num].chance,
                                     Producers[Pro_num].group, Consumers[Con_num].group,
                                     Consumers[Con_num].WillBehave, Consumers[Con_num].In])

            else:  # the producer has the opportunity to reject trades because it is not a new consumer
                # reject + not a new consumer

                Pun = -1  # this only to solve the error : NameError: name 'Pun' is not defined

                # This part has been added in 25 Sep
                ProRepPlot[Pro_num].append(Producers[Pro_num].score)
                ProTrade[Pro_num].append(i)
                # End of part 25 Sep

                with open('ProRepRecordConRun.csv', 'a') as t_file:
                    writer = csv.writer(t_file)
                    writer.writerow([i,
                                     Pro_num, Producers[Pro_num].score,
                                     Con_num, Consumers[Con_num].score,

                                     '*', '*', '*',

                                     '*', '*', Pun, Q,

                                     Producers[Pro_num].UnReTr, Producers[Pro_num].Reject, Response, timeout,

                                     Producers[Pro_num].NewConReject,

                                     Producers[Pro_num].Stops, Producers[Pro_num].TradeInvolved,

                                     '*', '*',
                                     'True', 'False',
                                     Producers[Pro_num].chance, Consumers[Con_num].chance,
                                     Producers[Pro_num].group, Consumers[Con_num].group,
                                     Consumers[Con_num].WillBehave, Consumers[Con_num].In])

            TSReset()
            flag = False
            UnReFlag = False
            ResponseReset()  # just test 16 sep









        # if ((ProChoice == 0) or (Response > timeout)):
        #     # that means he decides to reject the request -- 1 means accept the trade
        #     # Either reject or unreport  the trade request
        #
        #     TSUpdate(0)
        #
        #     # Reject the trade request
        #     if ( ProChoice == 0):
        #
        #         print " The producer has reject the trade request and should stop "
        #         print ' the producer score here is ', Producers[Pro_num].score
        #         Producers[Pro_num].Reject += 1
        #
        #
        #         print ' the Reject is for producer %2d'%Pro_num
        #         print ' is ', Producers[Pro_num].Reject
        #
        #
        #         if (Consumers[Con_num].score == 0):
        #             Producers[Pro_num].NewConReject +=  1
        #             flag = True
        #
        #             print ' the Reject is for producer %2d for new consumer ' % Pro_num
        #             print ' is ', Producers[Pro_num].NewConReject
        #
        #     # Unreport the trade request
        #     elif ( Response > timeout):
        #
        #         print " The producer has ignored the request ( the request is unreported) .. "
        #         print ' you will be panushed for the unreported request'
        #         unreportedRequest += 1
        #         Producers[Pro_num].UnReTr +=1
        #         UnReFlag = True
        #
        #         print ' the UR is for producer %2d' % Pro_num
        #         print ' is ', Producers[Pro_num].UnReTr
        #
        #
        #  # here we have to call the producer reputation method
        #
        #     # Start the reputtaion calculation for only :
        #     # 1- reject new consumer 2- Unreport request
        #     if ( UnReFlag or flag):
        #
        #
        #         print ' The producer TrV is :',Producers[Pro_num].TradeInvolved
        #
        #         if (Producers[Pro_num].TradeInvolved == 0):
        #
        #             # case 1:
        #             if (Producers[Pro_num].UnReTr == 0 and Producers[Pro_num].NewConReject == 1):
        #                 cur = 100
        #
        #             # case 2:
        #             elif (Producers[Pro_num].UnReTr == 1 and Producers[Pro_num].NewConReject == 0):
        #                 cur = 100
        #
        #             # case 3:
        #             elif (Producers[Pro_num].UnReTr >= 1 or Producers[Pro_num].NewConReject >= 1):
        #                 cur = 0
        #
        #
        #         elif (Producers[Pro_num].TradeInvolved > 0):
        #             cur = 0
        #
        #
        #
        #         print ' the curr after the section is :', cur
        #
        #         # adding the current the the Rew ( Update Raw)
        #         Producers[Pro_num].RawRep += cur
        #
        #         print ' the RawRep after adding the curr is :', Producers[Pro_num].RawRep
        #
        #         # Producer Reputation Calculation
        #
        #
        #         print ' the values before the reputation calculation as the following:'
        #         print ' TrV is : ', Producers[Pro_num].TradeInvolved
        #         print ' UnRe is :', Producers[Pro_num].UnReTr
        #         print ' NewConReject is :', Producers[Pro_num].NewConReject
        #
        #         Producers[Pro_num].score = round(Producers[Pro_num].RawRep / (
        #                     Producers[Pro_num].TradeInvolved + Producers[Pro_num].UnReTr + Producers[Pro_num].NewConReject), 2)
        #
        #         print " the updated producer score is ", Producers[Pro_num].score
        #
        #         Pun = -1  # this only to solve the error : NameError: name 'Pun' is not defined
        #
        #         with open('ProRepRecord.csv', 'a') as t_file:
        #             writer = csv.writer(t_file)
        #             writer.writerow([i,
        #                              Pro_num, Producers[Pro_num].score,
        #                              Con_num, Consumers[Con_num].score,
        #
        #                              '*', '*', '*',
        #
        #                              '*', '*', Pun,
        #
        #                              Producers[Pro_num].UnReTr, Producers[Pro_num].Reject,
        #
        #                              Producers[Pro_num].NewConReject,
        #
        #                              Producers[Pro_num].Stops, Producers[Pro_num].TradeInvolved,
        #
        #                              '*', '*', 'True', 'False',
        #                              Producers[Pro_num].chance, Consumers[Con_num].chance,
        #                              Producers[Pro_num].group, Consumers[Con_num].group,
        #                              Consumers[Con_num].WillBehave, Consumers[Con_num].In])
        #
        #     else: # the producer has the opportunity to reject trades because it is not a new consumer
        #         # reject + not a new consumer
        #
        #         Pun = -1  # this only to solve the error : NameError: name 'Pun' is not defined
        #
        #         with open('ProRepRecord.csv', 'a') as t_file:
        #             writer = csv.writer(t_file)
        #             writer.writerow([i,
        #                              Pro_num, Producers[Pro_num].score,
        #                              Con_num, Consumers[Con_num].score,
        #
        #                              '*','*', '*',
        #
        #                              '*', '*', Pun,
        #
        #                              Producers[Pro_num].UnReTr, Producers[Pro_num].Reject,
        #
        #                              Producers[Pro_num].NewConReject,
        #
        #                              Producers[Pro_num].Stops,Producers[Pro_num].TradeInvolved,
        #
        #                              '*', '*',
        #                              'True', 'False',
        #                              Producers[Pro_num].chance, Consumers[Con_num].chance,
        #                              Producers[Pro_num].group, Consumers[Con_num].group,
        #                             Consumers[Con_num].WillBehave, Consumers[Con_num].In])
        #
        #
        #     TSReset()
        #     flag = False
        #     UnReFlag = False

        else:  # This means the trade start and could be sucessed or failed ( SECTION 2 START )

            if (Consumers[Con_num].score == 0):
                # This to know he accept a new consumer request
                NewConReqUpdate(1)

            TA = TAGenerator(Consumers[Con_num].score)  # use the rep to set the BS

            #  ---------------------------------- Consumer Honest or Cheat (One Receipt)----------------------
            # here will decide if the consumer will cheat or be honest in this trade
            # ( at the begining of the trade)

            ConRep = Consumers[Con_num].score / 100.00
            rest = 1 - ConRep

            ProRep = Producers[Pro_num].score / 100.00
            Prest = 1 - ProRep

            #  --------------------------------Consumer Cheat or not ----------------------------------------

            # This part has been added on 14 Oct
            if (ConsumerFreChange == True):
                Consumers[Con_num].WillBehave = 'h'

            elif (ConRep == 1):
                # here if the consumer reputation is 100, then will add a small pro to could cheat
                # to avoid o be 100 for all time
                WillCheat = 1 / 100 * Consumers[Con_num].TradeInvolved
                Consumers[Con_num].WillBehave = np.random.choice(('h', 'c'), p=[(1 - WillCheat), WillCheat])
            else:
                Consumers[Con_num].WillBehave = np.random.choice(('h', 'c'), p=[ConRep, rest])
            # The end of the part has been added on 14 Oct

            if (Consumers[Con_num].WillBehave == 'c'):
                Consumers[Con_num].In = randint(1, TA['EBN'])  # choose which receipt he will cheat in

            elif (Consumers[Con_num].WillBehave == 'h'):
                Consumers[Con_num].In = -1

            #  --------------------------------Consumer Stop or not ----------------------------------------

            # Here I can add the part of stops baed on stop amount ( probability of the total)

            # This part has been added on 14 Oct
            if (ConsumerFreChange == True):
                Consumers[Con_num].WillStop = 'n'
            else:
                # # jana jana jana
                #
                # if (Consumers[Con_num].TradeInvolved == 0 ):
                #     WillStop = 0
                # else:
                #     WillStop = Consumers[Con_num].Stops / Consumers[Con_num].TradeInvolved
                #
                # # WillContinue = 1 - WillStop
                #
                # Consumers[Con_num].WillStop = np.random.choice(('y', 'n'), p=[WillStop, (1-WillStop)])
                # # The end of the part has been added on 14 Oct
                Consumers[Con_num].WillStop = np.random.choice(('y', 'n'), p=[rest, ConRep])

            if (Consumers[Con_num].WillStop == 'y'):
                Consumers[Con_num].WillStopIn = randint(1, TA['EBN'])  # choose which receipt he will stop after

            elif (Consumers[Con_num].WillStop == 'n'):
                Consumers[Con_num].WillStopIn = -1

                #  ---------------------------------- Producer Stop or not ----------------------
                # Just to avoid both P ,C will stop, we will go through this code in case consumer
                # will not stop
                # if ( Consumers[Con_num].WillStop == 'y'):
                #
                #     Producers[Pro_num].WillStop == 'n'
                #     Producers[Pro_num].WillStopIn = -1
                #
                # else:

                Producers[Pro_num].WillStop = np.random.choice(('y', 'n'), p=[ProRep, Prest])
                # Producers[Pro_num].WillStop = np.random.choice(('y', 'n'), p=[0.5, 0.5])# just test 16 Sep

                if (Producers[Pro_num].WillStop == 'y'):
                    Producers[Pro_num].WillStopIn = randint(1, TA['EBN'])  # choose which receipt he will stop after

                elif (Producers[Pro_num].WillStop == 'n'):
                    Producers[Pro_num].WillStopIn = -1
            # ---------------------------------------------------------------------------------------------

            # Simulation*****Simulation*******Simulation*****Simulation*******Simulation*****Simulation*******Simulation*****Simulation*******Simulation
            results = start(Pro_num, Con_num, TA, Times)

            # immediatly after finishing the i trade, reset the batch number and MsgDelivered by calling the method:
            BatchNumberReset()
            MsgDeliveredReset()
            ReceiptDeliveredReset()
            LPReset()
            NewConReqReset()
            # timeoutReset()

            print('The result[0] by globing the value of BacthNumber is ')
            print (results[0])

            print(' The value of BatchNumber after reset its value to 0 is ')
            print (BatchNumber)

            print ('The result[2] by globing the value of MsgDelivered is ')
            print (results[2])

            print (' The value of MsgDelivered after reset its value to 0 is ')
            print (MsgDelivered)

            print (' The number of LP is the trade is ')
            print (LPN)

            print ('The number of messages in last package is: ')
            print (LP)

            print (' The number of Msg in last package from the Monitor is ')
            print (results[4])

            # update the number of trades involved for both producer and consumer
            Producers[Pro_num].TradeInvolved = Producers[Pro_num].TradeInvolved + 1
            Consumers[Con_num].TradeInvolved = Consumers[Con_num].TradeInvolved + 1

            # results[0]:BN , results[1]:TotalTime (T)
            # The Process of calculating everything after the trade finish *********** The Process of calculating everything after the trade finish*******

            payment = TA['price'] * results[2]  # results[2] is the total msg number delivered by the consumer
            # This payment is the AP (Actula price) as in the doc

            window = TA['to'] - TA['from']

            if (results[1] > window):
                per = 100
            else:
                per = (results[1] * 100) / (TA['to'] - TA['from'])

            totalPrice = TA['price'] * (
                    TA['BS'] * results[0] + results[4])  # results[0]:BN -- TA['rate'] is the rate per unit

            print ' the total price is ', totalPrice
            # This is the TP ( total price ) as in the doc
            #
            # # AVG += totalPrice # we add everytime to calculate the avg :
            # AVGUpdate(totalPrice)

            # Calculate the local cost to be used in the punishment calculation
            Producers[Pro_num].TC += totalPrice
            if (payment == 0):

                Producers[Pro_num].AC += totalPrice
            else:
                Producers[Pro_num].AC += payment

            # HERE we have to add got and total for both producer and consumer

            # Here should add the reputation model I have

            # The start of the table of reputations Comparasion:----------------------------------

            '''It consists of 3 parts:
            A- msg delivered / total ( percentage of data delivered)
            B- the percetage of the time of ending the trade over TATI 
            C- this is the percentage of the price comparing to current trade price'''
            total = totalPrice / TA['price']

            a = results[2] / total * 100

            print ('the results[2] is: ', results[2])
            print ('the total is ', total)
            print ('the a is:', a)

            # b = results[1] * 100 /(TA['to'] - TA['from']) # timee / TATI
            b = results[1] * 100 / (TA['TATI'])  # timee / TATI

            print ' the first b is ', b

            print' TATI is ', TA['TATI']
            print ' the time taken is ', results[1]

            if (b > 100):
                b = 100

            print (' the b is :', b)

            # c= TA['price'] * 100 / HeigestTradePrice

            # print (' the c is : ', c)
            #
            # print (' the c log is : ', math.log(c))
            #
            # extra = round(math.log(c),2)

            CurrRep = round((a + b + (100 - b) * PS) / 2.0, 2)  # just to write the code

            # For row (1) in the table
            if (Consumers[Con_num].score >= 0.00 and Consumers[Con_num].score <= 25.00):

                if (CurrRep >= 0.00 and CurrRep <= 25.00):
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + CurrRep

                elif (CurrRep > 25.00 and CurrRep <= 50.00):
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + CurrRep * 1.02  # old 1.10

                elif (CurrRep > 50.00 and CurrRep <= 75.00):
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + CurrRep * 1.0267  # old 1.20

                elif (CurrRep > 75.00 and CurrRep <= 100.00):

                    temp = CurrRep * 1.03  # old 1.30
                    if (temp > 100.00):
                        temp = 100.00
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + temp


            # For row (2) in the table
            elif (Consumers[Con_num].score > 25.00 and Consumers[Con_num].score <= 50.00):

                if (CurrRep >= 0.00 and CurrRep <= 25.00):
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + CurrRep * 0.96  # old 0.90

                elif (CurrRep > 25.00 and CurrRep <= 50.00):
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + CurrRep

                elif (CurrRep > 50.00 and CurrRep <= 75.00):
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + CurrRep * 1.0134  # old 1.10

                elif (CurrRep > 75.00 and CurrRep <= 100.00):
                    temp = CurrRep * 1.02  # old 1.20
                    if (temp > 100.00):
                        temp = 100.00
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + temp


            # For row (3) in the table
            elif (Consumers[Con_num].score > 50.00 and Consumers[Con_num].score <= 75.00):
                if (CurrRep >= 0.00 and CurrRep <= 25.00):
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + CurrRep * 0.92  # old 0.80

                elif (CurrRep > 25.00 and CurrRep <= 50.00):
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + CurrRep * 0.98  # old 0.90

                elif (CurrRep > 50.00 and CurrRep <= 75.00):
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + CurrRep

                elif (CurrRep > 75.00 and CurrRep <= 100.00):
                    temp = CurrRep * 1.010  # old 1.10
                    if (temp > 100.00):
                        temp = 100.00
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + temp


            # For row (4) in the table
            elif (Consumers[Con_num].score > 75.00 and Consumers[Con_num].score <= 100.00):
                if (CurrRep >= 0.00 and CurrRep <= 25.00):
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + CurrRep * 0.88  # old 0.70

                elif (CurrRep > 25.00 and CurrRep <= 50.00):
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + CurrRep * 0.96  # old 0.80

                elif (CurrRep > 50.00 and CurrRep <= 75.00):
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + CurrRep * 0.0135  # 0.90

                elif (CurrRep > 75.00 and CurrRep <= 100.00):
                    temp = CurrRep * 1
                    if (temp > 100.00):
                        temp = 100.00
                    Consumers[Con_num].RawRep = Consumers[Con_num].RawRep + temp  # it already high so *1

            # --------------------------------------------------The table end

            print(" the old consumer score here is ")
            print (Consumers[Con_num].score)

            print ('the consumer currRep without any  multiplication is ', CurrRep)

            print (' the consumer RawRep after adding CurrentRep is ')
            print (Consumers[Con_num].RawRep)

            print ("the consumer TradeInvollved is : ")
            print (Consumers[Con_num].TradeInvolved)

            # Here we have to subtract the Pun ( if any )

            # # AVG = AVG / TradeSpace   no need this line becasuse we already calculate AVG in the method
            #
            # print ' The avg is : ', AVG

            if (PS):
                Pun = 0
            else:
                # cal the avg of local producer AC
                # Pun = round(((totalPrice - payment) * 100.00 / totalPrice) / 100.00 * (Producers[Pro_num].AC/Producers[Pro_num].TradeInvolved) , 2)
                Pun = Pun = round(((totalPrice - payment) * 100.00 / totalPrice), 2)
                # print ' the current is ',CurrRep
                # Pun = 100 - CurrRep

                # Pun = round ((totalPrice - payment) /100 * AVG ,2)  # pun = (TP - AP) /100 * avg

            Consumers[Con_num].RawRep = Consumers[Con_num].RawRep - Pun

            print ' the percentage of the punishment is ', (totalPrice - payment) * 100.00

            print ' the producer AP including the current trade is', Producers[Pro_num].AC

            print ' The pun is :', Pun

            Consumers[Con_num].score = round(Consumers[Con_num].RawRep / Consumers[Con_num].TradeInvolved, 2)

            print(" the new consumer score here is ")
            print(Consumers[Con_num].score)

            # -----------------------------  The Producer Reputation Calculation ---------------------------
            # SECTION 2

            Res = 100 - (float(Response) / float(timeout) * 100.00)  # time taken to respond (percentage)

            print ' response is ', Response
            print ' timeout is ', timeout

            x = b

            print "x is ", x

            # # add this if 24 Sep
            # if ( ProducerFreChange or ConsumerFreChange):
            #     Q =100

            if (PS):  # if he stop

                #  adding a probability here to acheive the optional part of the Quality value from consumer
                #  because in this case it is optional for a consumer to rate the data quality

                # Q = randint(50,100) # just for now change it to be 50,100 the old 0,100
                #  adding zero here to mean it is optional and consumer could not send any value
                #  and therfore, the value Q=0

                Q = randint(0, 5)  # add zero because it is ( Optional )

                # This part has been added in 17 Oct

                gh = randint(0, 9)
                gh = Pro_num

                if (gh == Pro_num):

                    if (i > 200 and i < (400)):
                        Q = randint(0, 2)
                    elif (i >= 400 and i < 600):
                        Q = randint(3, 5)
                    elif (i >= 600 and i < 800):
                        Q = randint(0, 3)
                    elif (i >= 800 and i < 1000):
                        Q = randint(0, 2)
                    elif (i >= 1000 and i < 1200):
                        Q = randint(3, 5)
                    elif (i >= 1200 and i < 1400):
                        Q = randint(0, 3)
                    elif (i >= 1400 and i < 1600):
                        Q = randint(0, 2)
                    elif (i >= 1600 and i < 1800):
                        Q = randint(3, 5)
                    elif (i >= 1800 and i <= 2000):
                        Q = randint(0, 3)
                    # The end of the part added in 17 Oct

                # # This part has been added in 24 Sep
                # Q = randint(3, 5)
                # # End of 24 Sep

                if (Q != 0):
                    Q = Q * 20

                print ' Q value when PS stop is :', Q

                """
                PS:

                Q = 0 - 5 ( Optional ) each rate ( 20 points ) and 0 means doest give a review 
                Res = r
                time = b 

                """

                ProCurr = round((Res + Q + x) / 3, 2)
                print ' PS is on'

            elif (CS):

                # Q = randint(50, 100) # just for now change it to be 50,100 the old 1,100
                Q = randint(1, 2)  # It is required ( zero not included

                # This part has been added in 17 Oct

                gh = randint(0, 9)
                gh = Pro_num

                # if (gh == Pro_num):
                #
                #     if (i > 200 and i < (400)):
                #         Q = randint(3, 5)
                #     elif (i >= 400 and i < 600):
                #         Q = randint(1, 5)
                #     elif (i >= 600 and i < 800):
                #         Q = randint(1, 5)
                #     elif (i >= 800 and i < 1000):
                #         Q = randint(1, 2)
                #     elif (i >= 1000 and i < 1200):
                #         Q = randint(3, 5)
                #     elif (i >= 1200 and i < 1400):
                #         Q = randint(1, 3)
                #     elif (i >= 1400 and i < 1600):
                #         Q = randint(1, 2)
                #     elif (i >= 1600 and i < 1800):
                #         Q = randint(3, 5)
                #     elif (i >= 1800 and i <= 2000):
                #         Q = randint(1, 3)
                #     # The end of the part added in 17 Oct

                # # This part has been added in 24 Sep
                # Q = randint(3, 5)
                # # End of 24 Sep

                Q = 50 + (Q * 10)

                print ' Q value when CS stop is :', Q

                """
                CS:

                Q = 50 + 1 - 5 ( Required ) each rate ( 10 points )
                Res = r
                time = 100 

                """

                ProCurr = round((Res + Q + 100) / 3, 2)
                print ' PS is off and CS is on'

            elif (TS):

                Q = randint(1, 2)  # It is required ( zero not included )

                # # This part has been added in 24 Sep
                # Q = randint(3, 5)
                # # End of 24 Sep

                # This part has been added in 17 Oct

                gh = randint(0, 9)
                gh = Pro_num

                # if (gh == Pro_num):
                #
                #     if (i > 200 and i < (400)):
                #         Q = randint(1, 2)
                #     elif (i >= 400 and i < 600):
                #         Q = randint(3, 5)
                #     elif (i >= 600 and i < 800):
                #         Q = randint(1, 3)
                #     elif (i >= 800 and i < 1000):
                #         Q = randint(1, 2)
                #     elif (i >= 1000 and i < 1200):
                #         Q = randint(3, 5)
                #     elif (i >= 1200 and i < 1400):
                #         Q = randint(1, 4)
                #     elif (i >= 1400 and i < 1600):
                #         Q = randint(1, 2)
                #     elif (i >= 1600 and i < 1800):
                #         Q = randint(1, 2)
                #     elif (i >= 1800 and i <= 2000):
                #         Q = randint(2, 3)
                #     # The end of the part added in 17 Oct

                Q = Q * 20

                print ' Q value the trade i success is :', Q

                """
                TS ( S ):

                Q = 1 - 5 ( Required ) each rate ( 20 points )
                Res = r
                time = 100 

                """

                ProCurr = round((Res + Q + 100) / 3, 2)
                print ' TS is success '

            elif (TS == 0 and CS == 0 and PS == 0):

                Q = randint(1, 2)  # It is required ( zero not included )

                # # This part has been added in 24 Sep
                # Q = randint(3, 5)
                # # End of 24 Sep

                # This part has been added in 17 Oct

                gh = randint(0, 9)
                gh = Pro_num

                # if (gh == Pro_num):
                #
                #     if (i > 200 and i < (400)):
                #         Q = randint(1, 5)
                #     elif (i >= 400 and i < 600):
                #         Q = randint(1, 5)
                #     elif (i >= 600 and i < 800):
                #         Q = randint(1, 5)
                #     elif (i >= 800 and i < 1000):
                #         Q = randint(1, 5)
                #     elif (i >= 1000 and i < 1200):
                #         Q = randint(3, 5)
                #     elif (i >= 1200 and i < 1400):
                #         Q = randint(1, 3)
                #     elif (i >= 1400 and i < 1600):
                #         Q = randint(1, 2)
                #     elif (i >= 1600 and i < 1800):
                #         Q = randint(1, 5)
                #     elif (i >= 1800 and i <= 2000):
                #         Q = randint(1, 5)
                #     # The end of the part added in 17 Oct

                Q = Q * 20

                print ' Q value when the trade is failed is :', Q

                """
                TS ( F ):

                Q = 1 - 5 ( Required ) each rate ( 20 points )
                Res = r
                time = 100 

                note: the Q here is 100 in the formula while the trade failed becuse the consumer cheats 
                so his rate will not affect the producer reputation and rather, the Q value will be used only
                in rating the data stream quality

                """

                ProCurr = round((Res + 100 + 100) / 3, 2)
                print ' TS is falied and !PS and !CS'

            print "ProCurr after one of the cases is: ", ProCurr

            # ----------------------------------- Produer Incentive here ----------------------
            # if (NewConReq == 1):
            #     FinalREp = round(ProCurr * 1.10, 2)
            # else:
            #     FinalREp = round(ProCurr, 2)
            # ---------------------------------------------------------------------------------

            # just for now ( this line would be commented in  case of the producer incentive uncomment
            FinalREp = round(ProCurr, 2)

            Producers[Pro_num].RawRep += FinalREp

            #  Producer Reputation Claculation

            # here in this line I either add or remove 0.01
            Producers[Pro_num].score = round(Producers[Pro_num].RawRep / (
                    Producers[Pro_num].TradeInvolved + Producers[Pro_num].UnReTr + Producers[Pro_num].NewConReject),
                                             2)

            print ' the new producer score is ', Producers[Pro_num].score

            # if Con_num == 0: # we want to record the trades of the 1st consumer to plot it

            # if (Con_num == 0):
            #     con0Rep.append(Consumers[Con_num].score)
            #     con0Trade.append(i)
            #
            # if (Pro_num == 0):
            #     pr0Rep.append(Producers[Pro_num].score)
            #     pr0Trade.append(i)

            ConRepPlot[Con_num].append(Consumers[Con_num].score)
            ConTrade[Con_num].append(i)

            ProRepPlot[Pro_num].append(Producers[Pro_num].score)
            ProTrade[Pro_num].append(i)

            # HERE calculating the cost of the trade ( smart contract invocation)

            costInUSD = (results[3] * GUA + GUS) * GP / 1000000000 * 202.70  # ReceiptN is results[3]

            # ----TRADE RECORDIG ----- TRADE RECORDIG -----TRADE RECORDIG -----TRADE RECORDIG -----TRADE RECORDIG -----TRADE RECORDIG -----

            tempTrade.id = i
            tempTrade.pro = Producers[Pro_num]
            tempTrade.con = Consumers[Con_num]
            tempTrade.TA = TA
            tempTrade.payment = payment
            tempTrade.total = totalPrice
            tempTrade.BN = results[0]
            tempTrade.TimeTaken = results[1]
            tempTrade.MsgN = results[2] * 100 / total
            tempTrade.ReceiptN = results[3]
            if (results[1] < window):
                tempTrade.status = 0
                TSUpdate(0)
            else:
                tempTrade.status = 1
                TSUpdate(1)

            with open('ProRepRecordConRun.csv', 'a') as t_file:
                writer = csv.writer(t_file)

                writer.writerow([i,
                                 Pro_num, Producers[Pro_num].score,
                                 Con_num, Consumers[Con_num].score,

                                 TA['TATI'], TA['EBN'], TA['BS'],

                                 b, TS, Pun, Q,

                                 Producers[Pro_num].UnReTr, Producers[Pro_num].Reject, Response, timeout,
                                 Producers[Pro_num].NewConReject,

                                 Producers[Pro_num].Stops, Producers[Pro_num].TradeInvolved,

                                 PS, CS, 'False', 'False',
                                 Producers[Pro_num].chance, Consumers[Con_num].chance,
                                 Producers[Pro_num].group, Consumers[Con_num].group,
                                 Consumers[Con_num].WillBehave, Consumers[Con_num].In])

            NewConReqReset()
            timeoutReset()
            ResponseReset()

            PSReset()
            CSReset()
            TSReset()

            # Reset Pun
            Pun = -1
    else:
        print " You are banned of doing a trade in this marketplace because of your reputation is less than zero"

        with open('ProRepRecordConRun.csv', 'a') as t_file:
            writer = csv.writer(t_file)
            writer.writerow([i,
                             Pro_num, Producers[Pro_num].score,
                             Con_num, Consumers[Con_num].score,

                             '*', '*', '*',

                             '*', '*', '*', Q,

                             Producers[Pro_num].UnReTr, Producers[Pro_num].Reject, Response, timeout,

                             Producers[Pro_num].NewConReject,

                             Producers[Pro_num].Stops, Producers[Pro_num].TradeInvolved,

                             '*', '*', 'False', 'True',
                             Producers[Pro_num].chance, Consumers[Con_num].chance,
                             Producers[Pro_num].group, Consumers[Con_num].group,
                             Consumers[Con_num].WillBehave, Consumers[Con_num].In])

            # TradeInfo.append(tempTrade)

            # ---------------------------------------------------

            # with open('TradeRecord.csv', 'a') as t_file:
            #     writer = csv.writer(t_file)
            #
            #     writer.writerow([tempTrade.id,
            #                      tempTrade.pro.id,tempTrade.pro.TradeInvolved,
            #                      tempTrade.con.id, CurrRep, tempTrade.con.score,tempTrade.con.TradeInvolved,
            #                      tempTrade.TA['from'],tempTrade.TA['to'],tempTrade.TA['rate'],tempTrade.TA['BS'],tempTrade.TA['price'],
            #                      tempTrade.status,tempTrade.BN,tempTrade.MsgN,tempTrade.ReceiptN,tempTrade.payment,tempTrade.total,tempTrade.TimeTaken, costInUSD])

    # The last step,, presenting the result of the full simulation******The last step,, presenting the result of the full simulation******

print('After %02d trade, the participants who taking part in these trades are:' % (i))

# MatPlotlib part*******MatPlotlib part*******MatPlotlib part*******MatPlotlib part*******MatPlotlib part*******MatPlotlib part*******


# pyl.plot(Trades,waitingTime)
# pyl.title("Consumer Waiting Time ",fontsize=12,fontweight="bold")
# pyl.xlabel("Trade",fontsize=9,fontweight="bold")
# pyl.ylabel("Time",fontsize=9,fontweight="bold")
# pyl.grid(True)
# pyl.show()


# -------------- Consumer Reputation and Cheating Correlation
# rep=[]
# hon=[]
#
# for i in range(Consumers.__len__()):
#     rep.append(Consumers[i].score)
#     hon.append(1 - (round(Consumers[i].score,2)/100.00))
#
# pyl.plot(rep,hon)
# pyl.title("Consumer Reputation and Cheating Correlation ",fontsize=12,fontweight="bold")
# pyl.xlabel("Reputation",fontsize=9,fontweight="bold")
# pyl.ylim(0,1)
# pyl.xlim(0,100)
# pyl.ylabel("Probability of Cheating",fontsize=9,fontweight="bold")
# pyl.grid(True)
# pyl.show()


# This plot for consumer reputation
for m in range(0, ParticipantSpace):
    con0.plot(ConTrade[m], ConRepPlot[m], '--.')
    con0.xlabel("Consumer %2d Trades Involved" % m)

    con0.axhspan(0, 25, alpha=0.5, color='red')
    con0.axhspan(25, 50, alpha=0.5, color='orangered')
    con0.axhspan(50, 75, alpha=0.5, color='orange')
    con0.axhspan(75, 100, alpha=0.5, color='seagreen')

    con0.ylabel("Reputation Score")
    # con0.ylim(0,100)

    # This part has been added in 24 Sep
    major_ticksX = np.arange(0, (TradeSpace + 1), 200)
    con0.xticks(major_ticksX)
    # End of 24 Sep
    con0.yticks([0, 25, 50, 75, 100], [0, 'Low (25)', 'Barely (50)', 'Good (75)', 'Honest (100)'], rotation='30')
    con0.grid(True)
    con0.show()

# This part for producer reputation
for n in range(0, ParticipantSpace):
    con0.plot(ProTrade[n], ProRepPlot[n], '--.')
    con0.xlabel("Producer %2d Trades Involved" % n)

    con0.ylabel("Reputation Score")

    # con0.ylim(top=100)

    # con0.ylim(0,100) # just test 16 Sep

    # this part 23 Sep
    major_ticksX = np.arange(0, (TradeSpace + 1), 200)
    major_ticksY = np.arange(0, 101, 10)

    con0.xticks(major_ticksX)
    con0.yticks(major_ticksY)

    # end this part 23 Sep

    con0.grid(True)
    con0.show()

# ----------------------------------------PRODUCER GROUPS ------------------------
# This part for producers group
for x in range(ParticipantSpace):
    if (Producers[x].group == 'h'):
        ProH.append((Producers[x].id))
    if (Producers[x].group == 'c'):
        ProC.append(Producers[x].id)

# -----------------------This part has been commented 17 Oct ( 2 seperate plots
# ---- for H , C producers
# ----------------------------------------------------
# # This part for producer H (group)
# labelsPH = []
# for n in range(len(ProH)):
#     P_H.plot(ProTrade[ProH[n]], ProRepPlot[ProH[n]])
#     labelsPH.append("Producer %2d" % ProH[n])
#
# P_H.legend(labelsPH, ncol=3, loc='lower center')
# P_H.title("Producers Group \'H\'")
# P_H.xlabel("Trades Involved")
# P_H.ylabel("Reputation Score")
# # P_H.ylim(top=100)
# # P_H.ylim(0,100) # just test 16 sep
#
# # this part 23 Sep
# major_ticksX = np.arange(0, (TradeSpace+1), 200)
# major_ticksY = np.arange(0, 101, 10)
#
# P_H.xticks(major_ticksX)
# P_H.yticks(major_ticksY)
#
# # end this part 23 Sep
#
# P_H.grid(True)
# P_H.show()
# #--------------------------------------------------
# # This part for producer C (group)
# labelsPC = []
# for n in range(len(ProC)):
#     P_C.plot(ProTrade[ProC[n]], ProRepPlot[ProC[n]])
#     labelsPC.append("Producer %2d" % ProC[n])
#
# P_C.legend(labelsPC, ncol=3, loc='lower center')
# P_C.title("Producers Group \'C\'")
# P_C.xlabel("Trades Involved")
# P_C.ylabel("Reputation Score")
# # P_C.ylim(0,100)
# # P_C.ylim(top=100)
#
# # this part 23 Sep
# major_ticksX = np.arange(0, (TradeSpace+1), 200)
# major_ticksY = np.arange(0, 101, 10)
#
# P_C.xticks(major_ticksX)
# P_C.yticks(major_ticksY)
#
# # end this part 23 Sep
#
# P_C.grid(True)
# P_C.show()
# ----------------------------------End of the part: seperate plots for 2 groups
# It is commented 17 Oct

# The start of the combined plot of all producer ( fixing producer evaluation) 17 Oct

labelsAllPro = []
for n in range(len(ProH)):
    All_Pro.plot(ProTrade[ProH[n]], ProRepPlot[ProH[n]])
    labelsAllPro.append("Opt. Pro %2d" % ProH[n])

for n in range(len(ProC)):
    All_Pro.plot(ProTrade[ProC[n]], ProRepPlot[ProC[n]])
    labelsAllPro.append("Ordinary Pro %2d" % ProC[n])

All_Pro.legend(labelsAllPro, ncol=3, loc='lower center')
All_Pro.title("Producers")
All_Pro.xlabel("Trades Involved")
All_Pro.ylabel("Reputation Score")
# P_H.ylim(top=100)
# P_H.ylim(0,100) # just test 16 sep

# this part 23 Sep
major_ticksX = np.arange(0, (TradeSpace + 1), 200)
major_ticksY = np.arange(0, 101, 10)

All_Pro.xticks(major_ticksX)
All_Pro.yticks(major_ticksY)

# end this part 23 Sep

All_Pro.grid(True)
All_Pro.show()

# ------------------------------------- CONSUMERS GROUP -------------------

# This part for consumers group
for x in range(ParticipantSpace):
    if (Consumers[x].group == 'h'):
        ConH.append((Consumers[x].id))
    if (Consumers[x].group == 'c'):
        ConC.append(Consumers[x].id)

# This part for Consumer H (Group)
labelsCH = []
for n in range(len(ConH)):
    C_H.plot(ConTrade[ConH[n]], ConRepPlot[ConH[n]])
    labelsCH.append("Consumer %2d" % ConH[n])

C_H.legend(labelsCH, ncol=3, loc='lower center')
C_H.axhspan(0, 25, alpha=0.5, color='red')
C_H.axhspan(25, 50, alpha=0.5, color='orangered')
C_H.axhspan(50, 75, alpha=0.5, color='orange')
C_H.axhspan(75, 100, alpha=0.5, color='seagreen')

# This part has been added in 24 Sep
major_ticksX = np.arange(0, (TradeSpace + 1), 200)
C_H.xticks(major_ticksX)
# End of 24 Sep

C_H.yticks([0, 25, 50, 75, 100], [0, 'Low (25)', 'Barely (50)', 'Good (75)', 'Honest (100)'], rotation='30')
C_H.title("Consumer Group \'H\'")
C_H.xlabel("Trades Involved")
C_H.ylabel("Reputation Score")
# C_H.ylim(0,100)
# C_H.ylim(top = 100)
C_H.grid(True)
C_H.show()

# This part for Consumer C (Group)
labelsCC = []
for n in range(len(ConC)):
    C_C.plot(ConTrade[ConC[n]], ConRepPlot[ConC[n]])
    labelsCC.append("Consumer %2d" % ConC[n])

C_C.legend(labelsCC, ncol=3, loc='lower center')
C_C.axhspan(0, 25, alpha=0.5, color='red')
C_C.axhspan(25, 50, alpha=0.5, color='Orangered')
C_C.axhspan(50, 75, alpha=0.5, color='orange')
C_C.axhspan(75, 100, alpha=0.5, color='seagreen')

# This part has been added in 24 Sep
major_ticksX = np.arange(0, (TradeSpace + 1), 200)
C_C.xticks(major_ticksX)
# End of 24 Sep

C_C.yticks([0, 25, 50, 75, 100], [0, 'Low (25)', 'Barely (50)', 'Good (75)', 'Honest (100)'], rotation='30')
C_C.title("Consumer Group \'F\'")
C_C.xlabel("Trades Involved")
C_C.ylabel("Reputation Score")
# C_C.ylim(0,100)
# C_C.ylim(top = 100)
C_C.grid(True)
C_C.show()

# Notes and Explanation Part*******Notes and Explanation Part*******Notes and Explanation Part*******Notes and Explanation Part*******
"""Calculating the waiting time of the consumer to receive all data batches in a trade:
    Ba1: BT
    BA2: RT + ACK + BT 
    BA3: RT + ACK + BT
             .
             .
             .
             .
    BN: ............

    Total Waiting Time = [BT + (RT + ACK + BT)*BN-1 ]"""

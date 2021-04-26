pragma solidity ^0.5.16;

contract MK  {

//  ----- enum declreation --------- enum declreation --------------- enum declreation -----------------------

enum TAstate { Created, Approved, Rejected, Faild, Success, InProgress, Expired}

//  ----------- Temp Decleration ------------ Temp Decleration ---------------- Temp Declreation --------------

address owner;
Offer[]  offers; // all offers
TradeAgreement temp;
Receipt r;
Offer o; //temp


// ----------- constructor -------------- constructor -------------- constructor --------------------------

constructor() public
{
owner = msg.sender;    
}

//  ---- Struct Declreation ---------- Struct Declreation ------- Struct Declreation --------------------

struct Offer
{
uint id;
address payable producer;
address payable  broker;
string  topic;
uint  rate; // message rate messages/time
string  start;
string  to;
uint up; // unit price ( cost per message)
// uint oct; // offer confirmation time 
bool valid; // show the offer state either true or false

}

struct Receipt
{
uint id; // its number 
uint TA_id; // the id of TA belongs to
uint Msg; 
uint quality;
}

struct Producer 
{
string name;
address payable add;
bool isAcon;

uint[] TAs;


uint TrV; // total trade involved in 
uint stops; 
uint RNC; // the number of rejected requests from new consumer 
uint UR; // the number of unreported messages

int TR; // out of 100 %

uint oct;

uint quality; // should add data quality somewhere
bool able;

} 

struct Consumer
{
string name;
address payable add;
bool isApro;
uint[] TAs; // list of all TA ids he did it
uint TrV; // total trade involved in 
uint stops; 
int TR; // out of 100 % will be multiplied by 100
bool canTrade;

uint Rz;
uint chance;

}

struct Broker 
{
string name;
address payable add;
}

struct TradeAgreement
{
    uint id;
    uint of_id;
    address payable producer;
    address payable broker;
    address payable consumer;
    
    string topic;
    uint rate;
    uint up;
    
    string start;
    string to;
    uint TATI;
    
    uint ETM; // Expected total message in the Trade
    
    uint BS;
    
    bool approvedByA;
    bool approvedByB; 

    Receipt[] receipts; // record all receipts sent by consumer 
 
    TAstate TAst; // to record the TA state 

    bool CS;
    bool PS;

    uint ATM; // actual msg
    uint RM;
    uint AT; // actual time 

    uint GP;
    uint RT;
}


//  ---- modifier ------------ modifier ------------ modifier ------------------- modifier --------------------

modifier onlyOwner () 
{
  require(msg.sender == owner);
  _;
}

modifier permitted ()
{
    require (consumers[msg.sender].canTrade == true);
    _;
}

modifier Pay_mod ()
{
    require (consumers[msg.sender].Rz == msg.value);
    _;
}

modifier chance_num()
{
	require (consumers[msg.sender].chance == 0);
	_;
}

modifier updateOf_mod(uint off_id)
{
    require (offers[off_id].producer == msg.sender);
    _; 
}

//  -------- mapping ------------- mapping ------------ mapping ---------------------------------------------

mapping ( uint => TradeAgreement) allTA; // mapped with its id
mapping (address  => Producer)  producers ;
mapping ( address => Consumer) consumers;
mapping ( address => Broker) brokers;


// ------------- Events --------------- Events ------------------ Events ---------------------------------------

// event reg_done(bool indexed _reg_done);
event mkOrderE (uint _TA_id, address payable  _p);
event ResponseE(address payable _c, uint _TA_id, bool _response);
event NewTAE(uint _TA_id,string _start,string _end);
event publishOffer (bool _isPublished,uint _offId);
event NewReceiptE(uint _TA_id, uint _RM, address payable _p, bool _terminate, bool _CS, uint _Q);
event PS(uint _TA_id, address payable _p);
event RzE (address c);


//  Get Functions ------------------- Get Functions -------------- Get Functions -----------------------------

function CheckAdd () view public returns (address payable _add,bool _p, bool _c, bool _b)
{
return (msg.sender,producers[msg.sender].add == msg.sender, consumers[msg.sender].add == msg.sender,brokers[msg.sender].add == msg.sender);
}


function getOwner() view public returns (address _owner)
{
return (owner);
} // end getOwner function 


function getOffersSize () view public returns (uint _size)
{
    return (offers.length);
}

function getOffer1 (uint _counter) view public returns (uint _id, address payable _p, address payable _broker, string memory _topic, uint _rate)
{

    return (offers[_counter].id, offers[_counter].producer, offers[_counter].broker, offers[_counter].topic,offers[_counter].rate);
}


function getOffer2 (uint _counter) view public returns (string memory  _start, string  memory _to, uint _up, bool _valid)
{
    return (offers[_counter].start, offers[_counter].to, offers[_counter].up,offers[_counter].valid);
}

function getTA1(uint _TA_id) view public returns(address payable _p, address payable _c, address payable _b, string memory _topic, uint _rate, uint _up)
{

return(allTA[_TA_id].producer,allTA[_TA_id].consumer,allTA[_TA_id].broker, allTA[_TA_id].topic,allTA[_TA_id].rate, allTA[_TA_id].up);

} // end getTA1 function 

function getTA2(uint _TA_id) view public returns(string memory _start, string memory _to, uint _TATI, uint _ETM, uint _BS)
{


return(allTA[_TA_id].start, allTA[_TA_id].to, allTA[_TA_id].TATI, allTA[_TA_id].ETM, allTA[_TA_id].BS);

} // end getTA2 function



function getTA3 (uint _TA_id) view public returns (bool app_A, bool app_B, TAstate _State, uint RT)
{

return(allTA[_TA_id].approvedByA, allTA[_TA_id].approvedByB, allTA[_TA_id].TAst, allTA[_TA_id].RT);

} // end getTA3 function


function getTA4 (uint _TA_id) view public returns (bool CS, bool _PS, uint ATM, uint AT, uint RM)
{

return(allTA[_TA_id].CS, allTA[_TA_id].PS, allTA[_TA_id].ATM, allTA[_TA_id].AT, allTA[_TA_id].RM );

} // end getTA4 function


function getProducer1(address payable _p) view public returns (string memory name, bool isAcon, uint Trv, uint stops, uint RNC, uint UR, int TR)
{

return (producers[_p].name, producers[_p].isAcon,producers[_p].TrV, producers[_p].stops, producers[_p].RNC, producers[_p].UR, producers[_p].TR);

} // end getProducer1 function 


function getProducer2(address payable _p) view public returns (uint oct, uint quality, bool able)
{

return (producers[_p].oct, producers[_p].quality, producers[_p].able);

} // end getProducer1 function 


function getProducer3(address payable _p, uint _i) view public returns (uint _TA_id)
{
  return(producers[_p].TAs[_i]);
}

function getProducerTASize(address payable _p) view public returns (uint _length)
{
return(producers[_p].TAs.length);
}

function getConsumer1 ( address payable _c) view public returns(string memory name, bool isApro, uint Trv, uint stops, int TR, bool canTrade)
{

return (consumers[_c].name, consumers[_c].isApro,consumers[_c].TrV, consumers[_c].stops, consumers[_c].TR, consumers[_c].canTrade);

} // end getConsumer1 function 

function getConsumer2 ( address payable _c) view public returns( uint Rz, uint chance)
{

return ( consumers[_c].Rz, consumers[_c].chance);

} // end getConsumer2 function 



function getConsumer3(address payable _c, uint _i) view public returns (uint _TA_id)
{
  return(consumers[_c].TAs[_i]);
}

function getConsumerTASize(address payable _c) view public returns (uint _length)
{
return(consumers[_c].TAs.length);
}

//  --------------- The main Functions --------------- The main Functions ------------- The main Functions -----

function register ( string memory nkname,uint code, bool _a) public
{

	address payable x = msg.sender;

if ( code == 101)
{
    
    producers[x].name = nkname;
    producers[x].add = x;
    producers[x].able = true;
    producers[x].TR = 10000;
    
    if (_a)
    {
      producers[x].isAcon = true;
      consumers[x].isApro = true;
    }
    
  // emit  reg_done(true);  

} // end if code == 101

else if ( code == 202)
{
    
    consumers[x].name = nkname;
    consumers[x].add = x;
    consumers[x].canTrade = true; // intialize the default value ( by default he can trade )
    
    if (_a)
    {
      consumers[x].isApro = true;
      producers[x].isAcon = true;
    }
    
  // emit  reg_done(true);  

} // end if code == 202

else if ( code ==303)
{
    
    brokers[x].name = nkname;
    brokers[x].add = x;
    
  // emit  reg_done(true);  

} // end if code == 303

}// end function register 


function offer (uint _id, address payable _broker, string memory _topic, uint _rate, string memory _start, string memory _to, uint _up, bool _valid)  public
{

        o.id = _id; 

        o.producer = msg.sender;
        o.broker = _broker;
        
        o.topic = _topic;
        o.rate = _rate;
        o.start = _start;
        o.to = _to;
        o.up = _up;
        // o.oct = _oct;
        o.valid = _valid;
        
        offers.push(o);
       
       emit publishOffer (true,o.id);

} // end offer function


function mkOrder (uint _of_id, address payable _p, address payable _b, string memory _top, uint _ra,string memory _start, string  memory _to, uint _u, uint TA_id, uint _BS, uint _ETM, uint _TATI,uint GP, uint RT) public payable permitted
{
    

    require (msg.value != (_ETM * (_u/100) * 1000000000000000000),"Total Trade cost and penalty ( if any) needed.. ");


    temp.id = TA_id;
    temp.of_id = _of_id;
    temp.producer = _p;
    temp.broker = _b;
    temp.consumer = msg.sender;
    temp.topic = _top;
    temp.rate = _ra;
    temp.up = _u;
    temp.start = _start;
    temp.to = _to;
    temp.TATI = _TATI;
    temp.ETM = _ETM;
    temp.BS =_BS;
    temp.approvedByB = true;
    temp.TAst = TAstate.Created;
    temp.GP = GP;
    temp.RT = RT;

    allTA[TA_id] = temp;
    producers[_p].TAs.push(TA_id);
    consumers[msg.sender].TAs.push(TA_id);

    emit mkOrderE(TA_id,_p);
// --------------------------------------------------

    } // end mkOrder function 


function AcceptTA (uint TA_id, uint _BS) public 
{

allTA[TA_id].approvedByA = true;

allTA[TA_id].BS = _BS;

allTA[TA_id].TAst = TAstate.Approved;

emit ResponseE(allTA[TA_id].consumer,TA_id, true);
emit NewTAE(TA_id,allTA[TA_id].start,allTA[TA_id].to);

} // end AcceptTA function 


function RejectTA (uint TA_id) public 
{

allTA[TA_id].TAst = TAstate.Rejected;

emit ResponseE(allTA[TA_id].consumer,TA_id, false);

} // end AcceptTA function 


function SendReceipt(uint _TA_id, uint Re_id, uint MsgCount, bool terminate , bool CS, uint Q) public 
{

r.id = Re_id;
r.TA_id = _TA_id;
r.Msg = MsgCount;
r.quality = Q;

allTA[_TA_id].receipts.push(r);

emit NewReceiptE(_TA_id, MsgCount, allTA[_TA_id].producer,terminate,CS,Q);


} // end SendReceipt function



function conTR (uint _TA_id, address payable con, uint _TrV, uint _stops, int _TR , bool _canTrade, uint _Rz) onlyOwner public
{

consumers[con].TAs.push(_TA_id);
consumers[con].TrV = _TrV;
consumers[con].stops = _stops;
consumers[con].TR = _TR;
consumers[con].canTrade = _canTrade;

// set Rz value 
consumers[con].Rz = _Rz;

if (_Rz > 0)
{
	consumers[con].canTrade = false;
}


} // end conTR function  


function proTR (uint _TA_id, address payable pro, uint _TrV, uint _stops, int _TR, uint _Q, uint _RNC, uint _UR) onlyOwner public
{

producers[pro].TAs.push(_TA_id);
producers[pro].TrV = _TrV;
producers[pro].stops = _stops;
producers[pro].TR = _TR;
producers[pro].quality = _Q;
producers[pro].RNC = _RNC;
producers[pro].UR = _UR;

} // end conTR function  

 //  Updates Functions ------------ Updates Functions ---------------- Updates Functions ---------------------



function updateTA(uint _TA_id, uint _State) onlyOwner public
{
allTA[_TA_id].TAst = TAstate(_State);

} // end updateTA function 

function setTA ( uint _TA_id,bool _CS, bool _PS, uint _ATM, uint _RM, uint _AT)  public onlyOwner
{


// producers[_p].add.transfer(_forPro);
// consumers[_c].add.transfer(_forCon);

allTA[_TA_id].CS = _CS;
allTA[_TA_id].PS = _PS;
allTA[_TA_id].ATM = _ATM;
allTA[_TA_id].RM = _RM;
allTA[_TA_id].AT = _AT;

// _p.transfer(_forPro);
// _c.transfer(_forCon);



// settle (_p,_c,_forPro,_forCon);

// _p.call.value(_forPro);
// _c.call.value(_forCon);

} // end getTA4 function

function settle ( address payable _p, address payable _c, uint _forPro, uint _forCon ) onlyOwner public
{
producers[_p].add.transfer(_forPro/100 ether);
consumers[_c].add.transfer(_forCon/100 ether);
}

function setOct (uint value) public
{
    producers[msg.sender].oct = value;

} // end setOct function 

function Set_PS(uint TA_id) public 
{

allTA[TA_id].PS = true;

emit PS(TA_id, msg.sender);

} // end stopTrade function 


// function Set_Rz(address _con, uint _Rz) public onlyOwner
// {
// 	consumers[_con].Rz = _Rz;
// }





uint amount = 0;
// address payable x;
function test1(address payable _x, address payable _y, uint period, uint uintPrice) public payable onlyOwner{


amount = period * uintPrice;

require ( amount == msg.value);

producers[_x].add = _x;
consumers[_y].add = _y;

}

// this function will be called after receiving RzE ( after consuer pay the Rz)
function permit (address con) public  onlyOwner
{
    consumers[con].canTrade = true;
    consumers[con].chance += 1;
    consumers[con].TR = 0;

}


function pay_Rz () public payable Pay_mod chance_num // can have the two modifier in one --> can do next step
{
	emit RzE (msg.sender);
} 


function t ( address con) public 
{
    consumers[con].TR = -23;
    consumers[con].Rz = 100;
    consumers[con].canTrade = false;
}


function updateAb (bool _ab) public
{
    producers[msg.sender].able = _ab;
}



function update_offer (uint _id, address payable _broker, string memory _topic, uint _rate, string memory _start, string memory _to, uint _up, bool _valid)  public  updateOf_mod (_id)
{
        // offers[_id].id = _id; 


        // require (offers[_id].producer == msg.sender);


        // o.id = _id; 

        // o.producer = msg.sender;
        // o.broker = _broker;
        
        // o.topic = _topic;
        // o.rate = _rate;
        // o.start = _start;
        // o.to = _to;
        // o.up = _up;
        // o.valid = _valid;
        
        // offers[_id] = o;
       

        // offers[_id].producer = msg.sender;
        offers[_id].broker = _broker;
        
        offers[_id].topic = _topic;
        offers[_id].rate = _rate;
        offers[_id].start = _start;
        offers[_id].to = _to;
        offers[_id].up = _up;
       
        offers[_id].valid = _valid;
}

// function test2(address payable _x, address payable _y, string memory value1, string memory value2) public onlyOwner{

function ropstenCheck () view public returns(address)
{
return owner;
}

function setRepTest(address x, int rep, bool dec) public onlyOwner
{
    if ( dec == true)
    {
        producers[x].TR = rep;
    }

    else

    {
        consumers[x].TR = rep;
    }
}
// 	producers[_x].add.transfer(value1);
// 	consumers[_y].add.transfer(value2);

// }

} // ond of MK contract

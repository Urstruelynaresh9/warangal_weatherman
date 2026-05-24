
import requests
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()

chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

# Replace with your NEW bot token
TOKEN = "bot8140465766:AAFcZkbv2uii6m0LVudr55cRHb0eG13t870"

URL = f"https://api.telegram.org/{TOKEN}/"

# Location to Station ID mapping
STATION_MAP = {
    "Moulali": 10001, "Sivaramapalle": 10002, "Medchal Industrial area sub-station": 10003,
    "Turkayamjal": 10005, "Jubileehills": 10006, "Airport": 10008, "Viratnagar DMRL": 10009,
    "Mamidipalle": 10010, "ESS Malkaram": 10011, "Musheerabad (chilkalguda)": 10012,
    "Bandlaguda": 10013, "Madhapur": 10014, "Dharmasagar": 10016, "Pargi": 10017,
    "Tandur": 10018, "Puttapahad": 10019, "Kodangal": 10020, "Maddur": 10021,
    "Mahabubnagar": 10022, "Marikal": 10023, "Makthal": 10024, "Amarachintha": 10025,
    "Gadwal": 10026, "Jadcherla": 10027, "Pullur": 10029, "Midjil": 10030,
    "Dagada": 10031, "Wanaparthy": 10032, "Kalwakurthy": 10033, "Nagarkurnool": 10037,
    "Kistampalle": 10040, "Achampet": 10042, "Kollapur": 10054, "Balanagar": 10057,
    "Shadnagar": 10059, "Kothur": 10060, "Bibinagar": 10068, "Hanmapur": 10070,
    "Kolanupaka": 10076, "Mothkur": 10081, "Shaligouraram": 10082, "Thungathurthi": 10086,
    "Balaram Thanda H/o Suryapet": 10093, "Narketpalle TRNSCO": 10097, "Choutuppal": 10100,
    "Mustyala": 10130, "Wadlakonda": 10131, "Raghunathpalle": 10133, "Patha Mancherial": 10135,
    "Dharmasagar": 10137, "Shantapur": 10138, "Mulugu Road": 10139, "Godkondla": 10140,
    "Marriguda": 10142, "Nasarlapalle Water Plant": 10144, "Patha Yellapur": 10145,
    "Akkapur": 10147, "Kondamallapally": 10148, "Chelpur": 10149, "Bhainsa": 10150,
    "Chinthagattu": 10151, "Kodandapuram Water Plant": 10152, "Pashamylaram": 10153,
    "Patha Rajampet": 10154, "Mulugu": 10155, "Kandi": 10157, "Adilabad Urban(Near GS Estate)": 10158,
    "Chalakurthy": 10160, "Lingampet": 10161, "Haliya": 10162, "Wardhannapet": 10164,
    "Nalgonda (SE Office TS TRANSCO)": 10165, "Hasanpalle": 10166, "Peddanagaram": 10167,
    "Zahirabad": 10168, "Ayyagaripalle": 10169, "Madugulapally": 10171, "Kollur": 10173,
    "Waddekothapalle": 10174, "Teekya Thanda": 10175, "Narayankhed": 10178, "Bhichkunda": 10179,
    "Minpoor ESS": 10182, "Bellal": 10183, "Mattampalle": 10184, "Shantinagar H/o Ananthagiri": 10188,
    "Gummadidala": 10190, "Janakampet": 10194, "Narsapur": 10195, "Ramannapeta": 10198,
    "Mangapet": 10199, "Ranjal": 10200, "Kowdipally": 10202, "Nizamabad": 10205,
    "Bhadrachalam (Sub Collector Office)": 10207, "Manuguru": 10209, "Rajpally": 10213,
    "Korutla": 10214, "Sitarampatnam": 10215, "Ch_Kondur": 10217, "Ramayampet": 10218,
    "Aswaraopeta": 10220, "Chegunta": 10222, "Lakmapoor": 10224, "Kataram": 10226,
    "Habshipur": 10229, "Perkit": 10230, "Siddipet": 10235, "Kusumanchi": 10236,
    "Mortad": 10238, "Tukkapur": 10240, "Bheemgal": 10243, "Prakash Nagar": 10245,
    "Sirikonda": 10248, "Kodakandla": 10249, "Manoharbad": 10252, "Dichpally": 10255,
    "Domakonda": 10257, "Malyalapalli": 10262, "Suglampalli": 10264, "Durshed": 10266,
    "Edulagattepalli": 10269, "Bornapalli": 10272, "Kothapalli-Dharmaram": 10274,
    "Husnabad": 10280, "Shanigaram": 10283, "Ellanthakunta": 10284, "Yellareddipeta": 10287,
    "Peddur": 10290, "Mallaram": 10293, "Penuballi": 10295, "Madhira": 10296,
    "Yellandu": 10297, "Laknepalle": 10298, "Nekkonda": 10299, "Godhuru": 10300,
    "Pudur": 10302, "Jagtial": 10303, "Endapally": 10305, "Buddeshpalli-Dharmapuri": 10306,
    "Guchibowli": 10308, "Amangal": 10309, "Ichoda": 10310, "Pochara": 10435,
    "Pippaldhari": 10500, "Arli (T)": 10501, "Lokari K": 10502, "Sirikonda (Tehsil Office)": 10503,
    "Allapalli": 10504, "Pentlam": 10505, "Karkagudem": 10506, "Sujathanagar": 10507,
    "Sirikonda": 10508, "Kannaigudem": 10509, "Sarvaipet": 10510, "Tekumatla": 10511,
    "Rajoli": 10512, "Pedda Kodapgal": 10513, "Malliala": 10514, "Pallegudem": 10515,
    "Lingapur (Tehsil Office)": 10516, "Yelkapalle": 10517, "Chinnagudur": 10518,
    "Gangaram": 10519, "Naspur": 10520, "ESS Bachpally": 10521, "ESS D.P.Pally": 10522,
    "Medipally(Municipal office)": 10523, "Sirsanagandla": 10524, "Mulkacharla": 10525,
    "Narsapur(G)": 10526, "Pakpatla": 10527, "Mendora": 10528, "Manikonda": 10529,
    "Nandigama (PHC)": 10530, "Mogdampalle": 10531, "Komuravelly": 10532, "Revally": 10533,
    "Kandikal Gate": 10534, "Maitrivanam": 10535, "Chityal (Tahsil Office)": 10536,
    "Karimnagar (Collectorate)": 10537, "Bheemini": 10538, "Kulcharam": 10539,
    "Vishwanathpet": 10540, "Vailpur": 10541, "Dharmaram": 10542, "Kamanpur": 10543,
    "Hayathnagar": 10544, "Jinnaram": 10545, "Sangareddy (Collectorate)": 10546,
    "Lakkavaram Road( ESS Huzur Nagar)": 10547, "Weepangandla": 10548, "Kothapalle": 10550,
    "Dilawarpur": 10625, "Lokeshwaram": 10626, "Chinthakani": 10627, "Chandampet": 10628,
    "Asifabad": 10629, "Bazarhathnoor": 10630, "Bejjur": 10631, "Kuntala": 10632,
    "Bela": 10633, "Bellampally": 10634, "Kannepalli": 10635, "Chennur": 10636,
    "Dahegaon": 10637, "Velganoor": 10638, "Gudihatnoor": 10639, "Heerapur": 10640,
    "Jainad": 10641, "Jainoor": 10642, "Jaipur": 10643, "Jannaram": 10644,
    "Kaddam Peddur": 10645, "Kagaznagar": 10646, "Kondapur": 10647, "Kerameri": 10648,
    "Kotapally": 10649, "Kouthala": 10650, "Kubeer": 10651, "Laxmanchanda": 10652,
    "Mamda": 10653, "Andugulapet": 10654, "Jam (Sainagar)": 10655, "Edbid": 10656,
    "Narnoor": 10657, "Nennel": 10658, "Neradigonda": 10659, "Rebbena": 10660,
    "Loanvelli": 10662, "Sirpur (U)": 10663, "Talamadugu": 10664, "Tamsi": 10665,
    "Tandur": 10666, "Tanur": 10667, "Tiryani": 10668, "Utnoor X Road": 10669,
    "Neelwai": 10670, "Wankidi": 10671, "Kanagal": 10672, "Yadagirigutta": 10673,
    "Buggabavi Guda (ESS Vemulapalle)": 10674, "Valigonda": 10675, "Matur": 10676,
    "Thirumalagiri": 10677, "Rajapet": 10678, "Jalal Pur (ESS Pochampalle)": 10679,
    "Penpahad": 10680, "Nidamanoor": 10681, "Nuthankal": 10682, "Narsaiahgudem H/o Dirsencherla": 10683,
    "Narayanapur": 10684, "Nampalle": 10685, "Nakrekal": 10686, "Nadigudem": 10687,
    "Gudapur": 10688, "Munagala": 10689, "Mamillagudem": 10690, "Mellachervu": 10691,
    "Mannevari Turkapalle": 10692, "Kethepalle": 10693, "Kattangoor": 10694, "Vemsoor": 10695,
    "Arvapalli H/o Jajireddigudem": 10696, "Gurrampode": 10697, "Dindi(Gundlapalle)": 10698,
    "Gundala": 10699, "Garidepalle": 10700, "Damaracherla": 10701, "Chendupatla": 10702,
    "Urumadla Road": 10703, "Chilkur": 10704, "Chandur": 10705, "Yacharam": 10706,
    "Bommalaramaram": 10707, "Atmakur": 10708, "Atmakur": 10709, "Athmakur": 10710,
    "Shayampet": 10711, "Bhupalpally": 10712, "Chennaraopet": 10713, "Chityal": 10714,
    "Devaruppula": 10715, "Dornakal": 10716, "Duggondi": 10717, "Eturunagaram": 10718,
    "Geesugonda": 10719, "Ghanpur (Stn)": 10720, "Govindaraopet": 10721, "Bachannapet": 10722,
    "Rebarthi": 10723, "Bhupathipet": 10724, "Khazipet": 10725, "Kesamudram": 10726,
    "Mangalavaripeta": 10727, "Kodakandla": 10728, "Kothaguda": 10729, "Lingalaghanpur": 10730,
    "Mahabubabad": 10731, "Mogullapally": 10732, "Nallabelly": 10733, "Narmetta": 10734,
    "Nellikudur": 10735, "Palakurthi": 10736, "Parkal (RDO Office)": 10737, "Kalleda": 10738,
    "Raiparthy": 10739, "Regonda": 10740, "Sangem": 10741, "Tadvai": 10742,
    "Thorrur": 10743, "Laxmidevipeta": 10744, "Zaffergadh": 10745, "Urus": 10746,
    "Shankarpalle": 10778, "Aswapuram": 10779, "Bayyaram": 10780, "Ravinoothala": 10781,
    "Burgampahad": 10782, "Maddukuru": 10783, "Satyanaryanapuram": 10784, "Mandalapally": 10786,
    "Dummugudem": 10787, "Enkuru": 10788, "Garla": 10789, "Gundala": 10790,
    "Madgul Chittempally": 10791, "Julurpad": 10792, "Kalluru": 10793, "Lingala": 10794,
    "Khanapur P.S": 10795, "Peddagopati": 10796, "Laxmidevipalli": 10797, "Mudigonda": 10800,
    "Mulakalapally": 10801, "Nelakondapalle": 10802, "E Bayyaram": 10803, "Sathupalle": 10804,
    "Karepalle (Gate)": 10805, "Tekulapalle": 10806, "Thallada": 10807, "Tirumalayapalem": 10808,
    "Nawabpet": 10809, "Alubaka(Z)": 10811, "Wazeed": 10812, "Wyra": 10813,
    "Kandukur": 10814, "Moinabad": 10815, "Dharur": 10816, "Singapur Township": 10817,
    "ESS Keesara": 10818, "Maheshwaram": 10819, "Arutla": 10820, "Manneguda": 10821,
    "Devarayamjal": 10822, "Salkarpet": 10823, "Doma": 10824, "Addakal": 10877,
    "Ieeja": 10878, "Amrabad": 10879, "Kondanagula": 10880, "Bhoothpur": 10881,
    "Bijinapalle": 10882, "Bomraspeta": 10883, "Chinna Chintha Kunta": 10884,
    "Damaragidda": 10885, "Devarakadra": 10886, "Dhanwada": 10887, "Doulthabad": 10888,
    "Ghanpur": 10889, "Ghattu": 10890, "Gopalpet": 10891, "Hanwada": 10892,
    "Kodandapur": 10893, "Keshampet": 10894, "Kodair": 10895, "Parpalli": 10896,
    "Kondurg": 10897, "Kanaipally": 10898, "Kosgi": 10899, "Lingal": 10900,
    "Madgul": 10901, "Maganoor": 10902, "Maldakal": 10905, "Jallapur": 10906,
    "Narayanpet": 10907, "Narva": 10908, "Nawabpet": 10909, "Pangal": 10910,
    "Pebbair": 10911, "Peddakothapalle": 10912, "Peddamandadi": 10913, "Yengampalli": 10914,
    "Veljala": 10915, "Telkapalle": 10916, "Thimmajipeta": 10917, "Uppununthala": 10918,
    "Utkoor": 10919, "Veldanda": 10920, "Waddepalle": 10921, "Alladurg": 10922,
    "Annasagar": 10923, "Asmanghad": 10924, "Rudraram(Gitam)": 10925, "Peddakodur": 10928,
    "Hathnoora": 10930, "Doultabad": 10931, "Tirumalagiri": 10932, "Vadi": 10933,
    "Munigadapa": 10934, "BHEL Factory": 10935, "Kondapur": 10936, "Jharasangam": 10937,
    "Kalher": 10938, "Kangti": 10939, "Kohir": 10940, "Kondapak": 10941,
    "Malchelma": 10942, "Manoor": 10943, "Mirdoddi": 10944, "Mulugu": 10945,
    "Sadasivpet": 10946, "Munipally": 10947, "Nangnoor": 10948, "Narlapur": 10949,
    "Nyalkal": 10950, "Pulkal": 10951, "Raikode": 10952, "Regode": 10953,
    "Shankarampet_A": 10954, "Shankarampet_R": 10955, "Shivampet": 10956, "Tekmal": 10957,
    "Rampur": 10958, "Gouraram": 10959, "Yeldurthy": 10960, "Mominpet": 10961,
    "Bantwaram": 10963, "Marpalle": 10974, "Basheerabad": 10975, "ESS Malkajgiri": 10976,
    "Basar": 10990, "Jambuga": 10991, "Kommera": 10992, "Kundaram": 10993,
    "Pembi": 10994, "ESS Balanagar": 10995, "Peddemul": 10997, "ESS Quthbullapur": 10998,
    "Shabad": 10999, "Ghanpur(NTPC)": 11000, "Yalal": 11001, "Bejjanki": 11076,
    "Bheemadevarapalle": 11077, "Boinpalle": 11078, "Marrigadda": 11079, "Chigurumamidi": 11080,
    "Arnakonda": 11081, "Eligaid": 11082, "Elkathurthy": 11083, "Gambhiraopeta": 11084,
    "Gangadhara": 11085, "Gollapalle P.S": 11086, "Julapalli": 11087, "Kalvacherla": 11088,
    "Kathlapur": 11089, "Tadikal": 11090, "Koheda": 11091, "Nizambad": 11092,
    "Gangipalli": 11093, "Mahadevpur": 11094, "Koyyur": 11095, "Mallapur": 11096,
    "Mallial": 11097, "Manthani": 11098, "Medipalle": 11099, "Metpalle": 11100,
    "Namapur": 11101, "Mutharam Mahadevpur": 11102, "Mutharam": 11103, "Odela": 11104,
    "Rangampalle": 11105, "Pegadapalle": 11106, "Raikal": 11107, "Gundi": 11108,
    "Venkepalli": 11109, "Sarangapur": 11110, "Srirampur": 11111, "Nustulapur": 11112,
    "Veenavanka": 11113, "Velgatoor": 11114, "Ankampalem": 11115, "Yerrupalem": 11118,
    "Yanambailu": 11119, "Golankonda": 11120, "Neredugommu": 11121, "Nemmani": 11122,
    "Addagudur": 11123, "Peddaveedu": 11124, "Junuthla": 11125, "Inavole": 11139,
    "Inugurthy": 11140, "Kolkonda": 11141, "Malkapur": 11142, "Padamati Keshavapur": 11143,
    "Lachapet": 11145, "Balkonda": 11146, "Bhiknoor": 11147, "Bibipet": 11148,
    "Tadwai": 11149, "Sadasivanagar": 11150, "Angadipeta": 11152, "Tirumalagiri_Sagar": 11153,
    "Birkoor": 11160, "Dharpally": 11161, "Gandhari": 11162, "Jakranpally": 11163,
    "Jukkal": 11164, "Kammarpally": 11165, "Kotgiri": 11166, "Menoor": 11167,
    "Nagireddypet": 11168, "Navipet": 11169, "Manchippa": 11170, "Pitlam": 11171,
    "Thumpally": 11172, "Chandur": 11173, "Yedapalle": 11174, "Machapur": 11175,
    "Shaikpet": 11189, "Gorrekunta": 11190, "West Maredpally": 11191, "Mondamarket": 11192,
    "Vittalvadi": 11194, "Srinagarcolony": 11195, "Asifnagar": 11196, "Bathukamma kunta ESS": 11197,
    "Chandulal Baradari (Opp. Zoo Park)": 11198, "Golkonda": 11199, "Nampally": 11200,
    "GHMC Office: Kukatpally": 11202, "Kapra (GHMC Office)": 11203, "L.B.Nagar (GHMC Office)": 11204,
    "Sardarmahal (zonal commissioner office)": 11206, "Khasimpet": 11257, "Janampeta": 11293,
    "Thothinonidoddi": 11294, "Kadthal": 11295, "Mudwin": 11296, "Rajapur": 11297,
    "Udithyal": 11298, "Kondareddipalle": 11299, "Manganur": 11300, "Dudyal": 11301,
    "Waddeman": 11302, "Mogalgidda": 11303, "Solipur": 11304, "Beechupalle(MPP School)": 11305,
    "Yellikal": 11306, "Dyagadoddi": 11307, "Dharur": 11308, "Alwalpad": 11309,
    "Thotapalle": 11310, "Sangam": 11311, "Thommidirekula": 11312, "Serivenkatapur": 11313,
    "Kasulabad": 11314, "Gundmal": 11315, "Williamkonda H/o Miraspally": 11316,
    "Arkapalle": 11317, "Machanpalle": 11318, "Burdipad": 11319, "Undavelly": 11320,
    "Urkonda": 11321, "Peddamudnur": 11322, "Kothapalle": 11323, "Thoodukurthy": 11324,
    "Kotakonda": 11325, "Chinnajatram": 11326, "Kolloor": 11327, "Remaddula": 11328,
    "Kethepally": 11329, "Chukkapur": 11330, "Peddur": 11331, "Bijwar": 11332,
    "Jatprole": 11333, "Velgonda": 11334, "Bollampalle": 11335, "Venkatapur": 11344,
    "Ainole": 11345, "Vankeshwar": 11346, "Palem (ARS)": 11347, "Donur": 11348,
    "Mogalamadka": 11349, "Jaklair": 11350, "Chennapuraopalle": 11351, "Madanapur (ARS)": 11352,
    "Chinna Thandrapadu": 11353, "Kummera": 11354, "Katkur": 11355, "Veltur": 11356,
    "Kothamolgara": 11357, "Argonda": 11358, "Aloor": 11359, "Issapalle": 11360,
    "Macherla": 11361, "Magidi": 11362, "Pulkal": 11363, "Saloora": 11364,
    "Gannaram": 11365, "Ramalakshmanpalle": 11366, "Sarvapur": 11367, "Konasamandar": 11368,
    "Manal": 11369, "Issaipet": 11370, "Dongli": 11371, "Somoor": 11372,
    "Madanpalle": 11373, "Tondakur": 11374, "Chimanpally": 11375, "Chinna Mavandhi": 11376,
    "Yergatla": 11377, "Koratpally": 11378, "Maqdumpur": 11379, "Ramareddy": 11380,
    "Rudrur (ARS)": 11381, "Wanalpahad": 11382, "Sonala": 11383, "Lingapur": 11384,
    "Bhoraj": 11385, "Lingapur": 11387, "Waddyal": 11388, "Abdullapur": 11389,
    "Ponkal": 11390, "Hajipur": 11391, "Ryali": 11392, "Mujigi": 11393,
    "Beeravelli": 11394, "Bharampur": 11395, "Jankapur": 11396, "Tandra": 11397,
    "Ramnagar (ARS)": 11399, "Bheemaram": 11400, "Buttapur": 11401, "Mudhole (ARS)": 11403,
    "Indurthy": 11457, "Vedurugattu": 11458, "Jaina": 11459, "Nerella": 11460,
    "Kandikatkoor": 11461, "Peddalingapuram": 11462, "Gajasingaram": 11463, "Burgupalle": 11464,
    "Gandipally": 11465, "Thangula": 11466, "Marripalligudem": 11467, "Kamalapur": 11468,
    "Asifnagar": 11469, "Kothagattu": 11470, "Thiramalapur": 11471, "Samudrala": 11472,
    "Marthanpeta": 11473, "Ailapur": 11474, "Kaleswaram": 11475, "Tadicherla": 11476,
    "Mallaram": 11477, "Raghavapeta": 11478, "Maddutla": 11479, "Gattududdenapalle": 11480,
    "Pochampalli": 11481, "Mannegudem": 11482, "Govindaram": 11483, "Jaggasagar": 11484,
    "Avunoor": 11485, "Regulagudem": 11486, "Palthem": 11488, "Allipur": 11489,
    "Akena Palli": 11490, "Eesala Thakkallapalli": 11491, "Ramagundam": 11492, "Kolvai": 11493,
    "Nerella": 11494, "Kanukula": 11495, "Renikunta": 11496, "Gullakota": 11497,
    "Maredupalli": 11498, "Vattemla": 11499, "Nampalle": 11500, "Veernapalli": 11501,
    "Rudrangi": 11502, "Peddampet": 11503, "Polasa (ARS)": 11504, "Jammikunta (ARS)": 11505,
    "Chinthakunta (ARS)": 11506, "Kunaram (ARS)": 11507, "Rajendranagar (ARS)": 11513,
    "Begumpet": 11514, "Pothareddipet": 11516, "Cheekode": 11523, "Kanduwada": 11548,
    "Chatlapally": 11551, "Angadi Kistapur": 11554, "Nallavalli": 11557, "Bejgaon": 11560,
    "Regulagadda (ESS Thummadam)": 11561, "Yacharam": 11562, "Venkiryal": 11563,
    "Maryala": 11564, "Pullemla": 11565, "Timmapur": 11567, "Mudigonda": 11568,
    "Padamati Palle": 11569, "Keethavarigudem H/o Raini Gudem": 11570, "Sharajpet": 11571,
    "Singaraj Palle": 11572, "Thirumalagiri": 11573, "Aiti Pamula": 11574,
    "Shivannagudem H/o Indurthi": 11575, "Eduluru": 11576, "Gondriyala": 11577,
    "Thogarrai": 11578, "Raghunadhapalem": 11579, "Donda Padu": 11580, "Urlugunda": 11581,
    "Dattappaguda (ESS Paladugu)": 11582, "P.Domalapalle": 11583, "Velugu Palle": 11584,
    "Medlavai": 11585, "Ghanpur": 11586, "Alangapuram": 11587, "Cheedella": 11588,
    "Pamukunta": 11589, "Yellanki": 11590, "Mamidala": 11591, "Pajjur": 11592,
    "Tekumatla": 11593, "Verkat Palle": 11594, "Tadkamalla": 11595, "Mootakondur": 11596,
    "Narketpalle": 11597, "Pulicherla": 11598, "Kamareddi Gudem": 11599, "Bollepalli": 11600,
    "Gaddipalle (ARS)": 11601, "Yerkaram": 11602, "Jangam": 11603, "Nagula Vancha": 11605,
    "Nagupalle": 11606, "Naidupeta": 11607, "Manchukonda": 11608, "Pangidi": 11609,
    "Konijerla": 11610, "Banapuram": 11611, "Pammi": 11612, "Gangaram": 11614,
    "Bachodu": 11616, "Siripuram": 11617, "Sadasivunipalem": 11621, "Malkaram": 11622,
    "Madhira (ARS)": 11623, "Wyra (ARS)": 11626, "Raghunathapalem": 11627, "Ammanagal": 11628,
    "Damera": 11629, "Peddapendyal": 11633, "Velair": 11634, "Perumandla Sankeesa": 11635,
    "Thatikonda": 11636, "Kondaparthy": 11637, "Nagaram": 11638, "Mallur": 11639,
    "Maripeda": 11640, "Medapalle": 11641, "Danthalapalle": 11642, "Munigalaveedu": 11643,
    "Gudur": 11644, "Enugal": 11645, "Venkatapur": 11646, "Kothapallegori": 11647,
    "Malyala (ARS)": 11648, "Kapulakanaparthy": 11649, "Velturlapalli": 11650, "Kunoor": 11651,
    "Kasimdevpeta": 11652, "Medaram": 11653, "Vavilala": 11655, "Kashibugga": 11656,
    "Upparagudem": 11657, "Kommulavancha": 11658, "Redlawada": 11659, "Pulakurthi": 11674,
    "Mallampalli": 11676, "Shapur Nagar": 11780, "ESS Jeedimetla": 11812, "Yerraram": 11814,
    "Pedda Shapur": 11823, "Chandanavally": 11824, "Abdullapurmet": 11825, "Reddy Palle": 11826,
    "Dandumailaram": 11827, "Mangalpalle": 11828, "Meerkhanpet": 11829, "Rachulur": 11830,
    "Chowdapur": 11831, "Mujahidpur": 11832, "Ameerpet": 11833, "Industrial area Mahankal": 11834,
    "Bodakonda": 11835, "Proddatur": 11836, "Bandamadharam": 11837, "Kethireddipalli": 11838,
    "Rapole": 11839, "Kotepally": 11840, "Peddaumanthal": 11841, "Tallapally": 11842,
    "Nagaram(Thorrimamidi)": 11843, "ESS Kesavaram": 11844, "Aliyabad": 11845,
    "Madanpalle": 11846, "Mohammadabad": 11847, "Nallavelli": 11848, "Dhavalapur": 11849,
    "Tandur(A) (ARS)": 11850, "Nagapur": 11851, "Thipparam": 11852, "Lakudaram": 11853,
    "Bujarampet": 11854, "Digwal": 11855, "Pathur": 11856, "Algole": 11857,
    "Gajwel (Tahsil Office)": 11858, "Gunegal(CRIDA)": 11859, "Satwar": 11860,
    "Kamkole": 11861, "Podichanpally ESS": 11862, "Chitkul": 11865, "Raghavapur": 11866,
    "Islampur": 11867, "Damarancha": 11868, "Almaipet": 11869, "Shivnooru ESS": 11873,
    "Kagazmaddur": 11874, "Kothapet": 11877, "Laxmapur ESS": 11878, "Venkatraopet": 11879,
    "Sardhana": 11880, "Lingaipalle": 11881, "Bodagat ESS": 11882, "Lakshmisagar": 11883,
    "Gundla Machanur": 11884, "Chippalturthi": 11885, "Dongala Dharmaram ESS": 11886,
    "Ramaram": 11887, "Kallakal": 11888, "Kurnavalli": 11889, "Gowraram": 11890,
    "Garimellapadu": 11891, "Thimmaraopeta": 11892, "Kakarvai": 11893, "Ravindranagar": 11894,
    "Vankulam": 11895, "Ginnedari": 11896, "Bhojannapet": 11897, "Gubbagurthy": 11898,
    "Mukundharpuram": 11899, "ESS Macha Bollaram": 11925, "Theldevarapalle": 11926,
    "University of Hyderabad": 11927, "Chaprala": 11929, "Devulawada": 11931,
    "Kollur": 11932, "Venkatraopet (GP Building)": 11933, "Eklaspur": 11958,
    "Bhadrachalam (Godavari Bank)": 11961, "Dharmavaram": 11962, "Padra (Police Station)": 11970,
    "Krishna": 11971, "Atmakur": 11972, "Polepallly": 11974, "Kaldurki": 11979,
    "Kashimpur": 11986, "Begumpet (IMD Office)": 12007, "Vikarabad": 12008,
    "Nalgonda (Collectorate Complex)": 12010, "Khammam (NSP Guest House)": 12011,
    "Jangaon": 12014, "WHITEGOLD 33/11 SS": 12017, "Medak_Rg (RDO Office)": 12018,
    "Paidipally (ARS)": 12024, "Mahabubnagar (Tehsil office)": 12025, "IDOC (Kamareddy)": 12026,
    "Adilabad Urban (Collectorate)": 12027, "Khanapur (Tahsil Office)": 12028, "Sircilla (IDOC)": 12030,
    "Sirpur (T) (Tehsil Office)": 12031, "Venkatapuram(Tahsil Office)": 12036,
    "Old Kothagudem": 12037, "Ibrahim Peta": 12046, "Ganaanka Bhavan": 12542,
    "Tharigoppula": 20001, "Alampur (Tahsil Office)": 20002, "Kaloor Timmanadoddi": 20003,
    "Nasrullabad": 20004, "Mupkal": 20005, "Nizamabad_North": 20006, "Palda": 20007,
    "Kistareddipet": 20008, "Mukthapur": 20009, "Sirgapoor": 20010, "Watpalle": 20011,
    "Reddiguda": 20012, "Nagaram": 20013, "Srirangapur": 20014, "Tadvai Huts": 30001,
    "Tapalpur": 30002, "Dulapally Forest Academy": 30003, "ESS Kondapur": 30004,
    "Vatwarlapally": 30005, "Chilkur Mrugvani": 30006, "Kadpal": 30007, "Mallapur": 30008,
    "Mulugu FCRI": 30009, "Eliminedu": 30010, "PHC Center, Ambedkar Nagar": 30011,
    "Community Hall, Telecom colony": 30012, "Jakora": 30013, "MPDO Office": 30014,
    "Malakpet Millath Comm Hall": 30015, "Ziaguda Ranganath Comm Hall (beside ranganatha temple)": 30018,
    "Football Ground Vijayanagar Colony": 30019, "Nadikuda": 30020,
    "Chandulal Baradari Sports Complex: Doodbowli": 30021, "Bandi Adda Community Hall: Gansibazar": 30022,
    "Kishanbagh Govt High School": 30023, "Setwin Training Center: Suleman Nagar": 30024,
    "Ferozguda Comm Hall: Balanagar": 30025, "Mothinagar Ward Office: Moosapet": 30026,
    "Community Hall, Fathe Nagar": 30027, "Chowtakur": 30028, "Bomandevipally": 30029,
    "Barkas ESS chandrayan gutta": 30030, "OWISI Commnuity Hall: Kanchanbagh": 30031,
    "Indiranagar Community Hall": 30032, "Balashetty Water Tank Building(HMWS): Dabeerpura": 30033,
    "Libraray Building: ReinBazar Yakuthpura SRT colony": 30034, "Vempalle": 30035,
    "GHMC Welfare Office: Shaikpet": 30036, "Golkonda Tasil office: Lungerhouse": 30037,
    "Pedda Amberpet Hanuman Temple": 30038, "Thorrur Gram Panchayat": 30039,
    "Pasumamula": 30040, "Lingojiguda Ward Office": 30041,
    "Prashanth Nagar Comm Hall: Vanasthalipuram": 30042,
    "South Hasthinapuram South Comm Hall": 30043, "Malkapur": 30044, "Gopannapally": 30045,
    "Kushaiguda old ward office: Cherlapalli": 30047, "Maheshnagar Ward Office: Dr.A.S.Rao Nagar": 30048,
    "Dammaiguda Municipal Council Building: Bandlaguda": 30050, "Dr.MCRHRD IT Campus": 30051,
    "Pillidarga Ward Office: Borabanda": 30052, "Yousufguda Zonal Commissioner officr": 30053,
    "Community Hall, CBCID Colony: KPHB": 30055, "PHC Center, Balaji Nagar": 30056,
    "Janampet": 30058, "Bheemavaram": 30059, "ESS HMT hills: Hyder Nagar": 30060,
    "Ward Office, Allapur Vivekananda Nagar": 30061,
    "Prasanth Nagar Community Hall: East Anandbagh": 30063,
    "Madhusudhan Nagar Comm.Hall: Anandbagvangah": 30064,
    "Vivekanandapuram Comm Hall: Neredmet": 30065, "Sultanpur": 30066,
    "Addagutta Community Hall": 30067, "Community Hall, Lalapet Moulali": 30068,
    "Seethapalmandi Kindi Basthi Comm Hall": 30070, "Pikit Govt. Primary School": 30071,
    "PHC Center, Peerzadiguda": 30072, "Mukundapuram": 30073, "Bansilalpet": 30074,
    "Osmania University Registrar Office": 30075, "Begum Bazar Doodh Khana UHC": 30077,
    "LB Stadium: Gunfoudry": 30078, "Dogs Control Building:Gowliwada Jumerath Bazar": 30079,
    "Dulmitta": 30080, "Patancheruvu Tahsil Office": 30081,
    "Community Hall, Aadharsh Nagar": 30082, "Palvatla": 30083, "Phanigiri": 30084,
    "Ward Office, Gayatri Nagar": 30085, "ESS Gajularamaram": 30086,
    "GHMC Circle office: Rajendranagar": 30088, "RDO Office: Attapur": 30089,
    "Near Ekta Colony: Shastripuram (Sivarampally)": 30091,
    "Sub Staion: Mailardevpally: Sivarampally": 30092, "Narayanraopet": 30093,
    "DEO office Beside Substaion: R.C.Puram": 30094, "Vinay Nagar Comm Hal: I.S.Sadan": 30095,
    "Mosra": 30096, "Dasturabad": 30097, "Govt. Boys High School: Kurmaguda": 30098,
    "Alakapuri Comm Hall": 30099, "Madhura nagar Comm.Hall": 30100,
    "Rock Town Colony: Nagole": 30101, "Thatiannaram": 30102, "Patigadda": 30103,
    "Raidurga Ward Office: Gachibowli": 30104, "Kakatiya Hills: Madhapur": 30105,
    "JPN Nagar Comm Hall: Miyapur": 30106, "Urban Health Centre: Hafeezpet": 30107,
    "MMTS Lingampally": 30109, "PJR Stadium: Chandanagar": 30110,
    "Khajaguda Sports Complex Gachibowli": 30111, "Tolichowki Dalith Bhavan": 30112,
    "Venkateshwara Colony: Banjarahills": 30113, "CMTC Premises: Banjara Hills": 30114,
    "Goutham Nagar Function Hall: Filmnagar": 30115, "Venkatgiri Water Tank: Vengalrao Nagar": 30116,
    "Rajiv Nagar Community Hall": 30117, "Ward Office, Mallapur": 30118,
    "Chilkanagar Comm Hall": 30119, "Abudulnagaram": 30120,
    "Maruthi Nagar Mahila Sabha Center": 30121, "New Nagole Welfare asscoiation": 30122,
    "Community Hall, Habsiguda JSN Colony": 30123, "Ramanthapur Ward Office": 30124,
    "Nacharam Ward Office": 30125, "Sakhi Center, Safilguda": 30126, "GHMC Head Office": 30127,
    "CESS": 30128, "Allabada Water Reservoir": 30129, "Mehdipatnam Navodaya Comm Hall": 30130,
    "Pothangal": 30131, "Saterla": 30132, "Koukuntla": 30133, "Nizampet": 30134,
    "Madikonda": 30135, "Elupugonda": 30136, "Kunchavelli": 30137, "Dhanora": 30138,
    "Sathnala": 30139, "New Mettuguda Primary School": 30140,
    "Khalender Nagar Community Hall": 30141, "Palton Community Hall": 30142,
    "Azampura Ward Office": 30143, "Edi bazar Community hall": 30144,
    "Rooplal Bazar Community Hall": 30145, "Wadi E Mahmood Sulemannagar, Pillar No.217": 30146,
    "Mekalamandi Community Hall": 30147, "Moosarambagh Ward office": 30148,
    "GHMC Zonal Office, Charminar Zone, Phool Bagh": 30149,
    "V.V Palem IDOC Collectorate office": 30150, "HMWSSB office RIYASATNAGAR": 30151,
    "IDOC Kongarkalan": 30152, "Collectorate Complex IDOC": 30153,
    "Ward Office, Karwan, Beside UPHC": 30154,
    "Bada Bazar Comm Hall, First Lancer, Ahmed Nagar": 30155,
    "Rajiv Gruhakalpa": 30157, "Shamshiguda": 30158, "Aviation Academy, Nadargul": 30159,
    "Kukatpally Village (Basthi Dawakhana)": 30160, "Bowenpally ward office": 30161,
    "GHMC Ward Office,Mahadevapuram": 30162, "Ward Office Building,SBI Colony Champapet": 30163,
    "GHMC Zonal Office, Uppal": 30164, "Defence Colony Comm Hall,  Hayath Nagar": 30165,
    "Model Market Bldg NGOs Colony, Vansathalipuram": 30166, "GHMC Transport Building": 30167,
    "Sainikpuri Shopping Complex": 30168, "Jawahar Nagar Community Hall": 30169,
    "Talla Basthi Community Hall": 30170, "TSRTC Employee Building, Vidya Nagar": 30171,
    "Ward Office, Nehru Nagar": 30172, "Bholakpur Comm Hall, Near  Musheerabad PS": 30173,
    "GHMC Sports Complex, Amberpet": 30174, "Vinayak Nagar Ward office": 30175,
    "Adikmet Ward office": 30176, "Boudha Nagar Community Hall": 30177,
    "MCH Colony, Library Building": 30178, "Old Ward Office ,Rahmathnagar": 30180,
    "Old sultan nagar Community hall": 30181, "Yadadri Bhuvanagiri Collectorate": 30182,
    "JVR OCP I&II": 40001, "GM Office-Manuguru": 40002, "24 Area, Yellandu": 40003,
    "Koyagudem": 40004, "RG-III,Mulakalapally": 40005, "GM-Office,Srirampur": 40006,
    "Yedula": 40007, "Solar Power Plant,Near Palachettu": 40009,
    "RG-2 at 8 in Cline Colony": 40010, "Goleti Township Singareni": 40011,
    "NC-8 Quarter building Pilot Colony": 40012, "GM Office 3 incline": 40013,
}

offset = 0

def get_weather_data(station_id=10272):
    """Fetch weather data from website using station ID"""
    try:
        weather_url = f'https://tgdps.telangana.gov.in/live.jsp?s1={station_id}'
        response = requests.get(weather_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table
        table = soup.find('table')
        
        weather_data = {}
        
        if table:
            # Iterate through table rows
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    weather_data[label] = value
        
        # Extract specific fields
        location = weather_data.get('AWS Location', 'N/A')
        mandal = weather_data.get('Mandal Name', 'N/A')
        temp = weather_data.get('Temperature', 'N/A')
        humidity = weather_data.get('Humidity(%)', 'N/A')
        rainfall = weather_data.get('Rainfall* (mm)', 'N/A')
        last_updated = weather_data.get('Last Updated', 'N/A')
        
        weather_text = f"""Weather Update for {location}:
Temperature: {temp}°C 🌤️
        """
#Location: {location}
#Mandal: {mandal}
#Humidity: {humidity}%
#Rainfall: {rainfall}mm
#Last Updated: {last_updated}        
        
        return weather_text
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

def get_weather_by_location(location_name):
    """Fetch weather data by location name"""
    # Normalize the location name (case-insensitive search)
    location_lower = location_name.lower().strip()
    
    # Find matching station
    station_id = None
    matched_location = None
    
    for loc_key, station in STATION_MAP.items():
        if loc_key.lower() == location_lower:
            station_id = station
            matched_location = loc_key
            break
    
    if not station_id:
        # Try substring match
        for loc_key, station in STATION_MAP.items():
            if loc_key.lower() in location_lower or location_lower in loc_key.lower():
                station_id = station
                matched_location = loc_key
                break
    
    if station_id:
        return get_weather_data(station_id)
    else:
        locations_list = "\n".join([f"• {loc}" for loc in sorted(STATION_MAP.keys())])
        return f"""❌ Location "{location_name}" not found.

Available locations:
{locations_list}"""

print("Bot is running...")

while True:
    response = requests.get(
        URL + "getUpdates",
        params={
            "timeout": 100,
            "offset": offset
        }
    )


    if response.status_code != 200:
        print(f"API Error: {response.status_code}")
        time.sleep(5)
        continue

    data = response.json()
    
    if not data.get("ok", False):
        print(f"API Error: {data.get('description', 'Unknown error')}")
        time.sleep(5)
        continue
    
    if "result" not in data:
        print("No 'result' in response")
        time.sleep(5)
        continue

    for update in data["result"]:

        offset = update["update_id"] + 1

        message = update.get("message")

        if not message:
            continue

        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        text_lower = text.lower()

        # Auto reply logic
        if text_lower == "w" or text_lower == "weather update":
            print("Getting default weather data for Bornapalli")
            reply = get_weather_data()
        elif text_lower == "list":
            # Show available locations
            locations_list = "\n".join([f"• {loc}" for loc in sorted(STATION_MAP.keys())])
            reply = f"""📍 Available Weather Stations:

{locations_list}

Send any location name to get current weather!"""
        else:
            # Check if user sent a location name
            print(f"Checking for location: {text}")
            reply = get_weather_by_location(text)

        # Send reply
        requests.get(
            URL + "sendMessage",
            params={
                "chat_id": chat_id,
                "text": reply
            }
        )

    time.sleep(1)

from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "Warangal Weather Bot Running"

def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

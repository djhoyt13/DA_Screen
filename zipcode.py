zipcodes = [
    "32003", "32008", "32009", "32011", "32024", "32025", "32033", "32034", "32038", "32040",
    "32043", "32044", "32046", "32052", "32053", "32054", "32055", "32058", "32059", "32060",
    "32062", "32063", "32064", "32065", "32066", "32068", "32071", "32073", "32080", "32081",
    "32082", "32083", "32084", "32086", "32087", "32091", "32092", "32094", "32095", "32096",
    "32097", "32099", "32102", "32110", "32112", "32112", "32113", "32114", "32117", "32118",
    "32119", "32124", "32127", "32128", "32129", "32130", "32131", "32132", "32134", "32134",
    "32136", "32139", "32140", "32141", "32145", "32148", "32159", "32162", "32168", "32169",
    "32174", "32176", "32177", "32179", "32180", "32181", "32181", "32187", "32189", "32190",
    "32193", "32193", "32193", "32195", "32198", "32202", "32204", "32205", "32206", "32207",
    "32208", "32209", "32210", "32211", "32212", "32214", "32216", "32217", "32218", "32219",
    "32220", "32221", "32222", "32223", "32224", "32225", "32226", "32227", "32233", "32234",
    "32244", "32246", "32250", "32254", "32256", "32257", "32258", "32259", "32266", "32277",
    "32301", "32303", "32304", "32305", "32306", "32307", "32308", "32309", "32310", "32311",
    "32312", "32313", "32317", "32320", "32321", "32322", "32324", "32327", "32328", "32331",
    "32332", "32333", "32334", "32336", "32340", "32343", "32344", "32346", "32347", "32348",
    "32350", "32351", "32352", "32358", "32359", "32399", "32401", "32403", "32404", "32405",
    "32407", "32408", "32409", "32413", "32420", "32421", "32423", "32424", "32425", "32425",
    "32425", "32426", "32427", "32428", "32430", "32431", "32433", "32435", "32437", "32438",
    "32439", "32440", "32442", "32443", "32444", "32445", "32446", "32448", "32449", "32455",
    "32456", "32459", "32460", "32461", "32462", "32464", "32465", "32466", "32501", "32502",
    "32503", "32504", "32505", "32506", "32507", "32508", "32509", "32511", "32512", "32514",
    "32520", "32521", "32526", "32531", "32533", "32534", "32535", "32536", "32539", "32541",
    "32542", "32547", "32548", "32550", "32559", "32561", "32563", "32564", "32565", "32566",
    "32567", "32568", "32569", "32570", "32571", "32577", "32578", "32579", "32580", "32583",
    "32601", "32603", "32605", "32606", "32607", "32608", "32609", "32610", "32611", "32612",
    "32615", "32617", "32618", "32619", "32621", "32622", "32625", "32626", "32628", "32631",
    "32640", "32641", "32643", "32648", "32653", "32656", "32666", "32667", "32668", "32669",
    "32680", "32686", "32693", "32694", "32696", "32701", "32702", "32703", "32707", "32708",
    "32709", "32712", "32713", "32714", "32720", "32723", "32724", "32725", "32726", "32730",
    "32732", "32735", "32736", "32738", "32744", "32746", "32750", "32751", "32754", "32757",
    "32759", "32763", "32764", "32765", "32766", "32767", "32771", "32773", "32776", "32778",
    "32779", "32780", "32784", "32789", "32792", "32796", "32798", "32801", "32803", "32804",
    "32805", "32806", "32807", "32808", "32809", "32810", "32811", "32812", "32814", "32816",
    "32817", "32818", "32819", "32820", "32821", "32822", "32824", "32825", "32826", "32827",
    "32828", "32829", "32831", "32832", "32833", "32834", "32835", "32836", "32837", "32839",
    "32885", "32886", "32887", "32891", "32896", "32897", "32899", "32901", "32903", "32904",
    "32905", "32907", "32908", "32909", "32919", "32920", "32922", "32926", "32927", "32931",
    "32934", "32935", "32937", "32940", "32948", "32949", "32950", "32951", "32952", "32953",
    "32955", "32958", "32960", "32962", "32963", "32966", "32967", "32968", "32976", "33004",
    "33009", "33010", "33012", "33013", "33014", "33015", "33016", "33018", "33019", "33020",
    "33021", "33023", "33024", "33025", "33026", "33027", "33028", "33029", "33030", "33031",
    "33032", "33033", "33034", "33035", "33036", "33037", "33039", "33040", "33042", "33043",
    "33050", "33054", "33055", "33056", "33060", "33062", "33063", "33064", "33064", "33065",
    "33066", "33067", "33068", "33069", "33070", "33071", "33073", "33076", "33106", "33109",
    "33109", "33112", "33122", "33125", "33126", "33127", "33128", "33129", "33130", "33131",
    "33132", "33133", "33134", "33135", "33136", "33137", "33138", "33139", "33140", "33140",
    "33141", "33141", "33142", "33143", "33144", "33145", "33146", "33147", "33149", "33150",
    "33154", "33154", "33155", "33156", "33157", "33158", "33160", "33161", "33162", "33165",
    "33166", "33167", "33168", "33169", "33170", "33172", "33173", "33174", "33175", "33176",
    "33177", "33178", "33179", "33180", "33181", "33182", "33183", "33184", "33185", "33186",
    "33187", "33188", "33189", "33190", "33191", "33192", "33193", "33194", "33195", "33196",
    "33198", "33199", "33206", "33301", "33304", "33305", "33306", "33308", "33309", "33311",
    "33312", "33313", "33314", "33315", "33316", "33317", "33319", "33321", "33322", "33323",
    "33324", "33325", "33326", "33327", "33328", "33330", "33331", "33332", "33334", "33336",
    "33337", "33351", "33388", "33394", "33401", "33403", "33404", "33405", "33406", "33407",
    "33408", "33409", "33410", "33411", "33412", "33413", "33414", "33415", "33417", "33418",
    "33426", "33428", "33430", "33431", "33432", "33433", "33434", "33435", "33436", "33437",
    "33438", "33440", "33441", "33442", "33444", "33445", "33446", "33449", "33455", "33458",
    "33460", "33461", "33462", "33463", "33464", "33467", "33469", "33470", "33471", "33472",
    "33473", "33476", "33477", "33478", "33480", "33483", "33484", "33486", "33487", "33493",
    "33496", "33498", "33499", "33510", "33511", "33513", "33514", "33523", "33525", "33527",
    "33534", "33538", "33540", "33541", "33542", "33543", "33544", "33545", "33547", "33548",
    "33549", "33556", "33558", "33559", "33563", "33565", "33566", "33567", "33569", "33570",
    "33572", "33573", "33576", "33578", "33579", "33584", "33585", "33592", "33594", "33596",
    "33597", "33598", "33602", "33603", "33604", "33605", "33606", "33607", "33609", "33610",
    "33611", "33612", "33613", "33614", "33615", "33616", "33617", "33618", "33619", "33620",
    "33621", "33624", "33625", "33626", "33629", "33633", "33634", "33635", "33637", "33647",
    "33650", "33655", "33660", "33661", "33662", "33663", "33664", "33701", "33702", "33703",
    "33704", "33705", "33706", "33707", "33708", "33709", "33710", "33711", "33712", "33713",
    "33714", "33715", "33716", "33729", "33730", "33755", "33756", "33759", "33760", "33761",
    "33762", "33763", "33764", "33765", "33767", "33769", "33770", "33771", "33773", "33774",
    "33776", "33777", "33778", "33781", "33782", "33785", "33786", "33801", "33803", "33805",
    "33809", "33810", "33811", "33812", "33813", "33815", "33823", "33825", "33827", "33830",
    "33834", "33837", "33838", "33839", "33841", "33843", "33844", "33849", "33850", "33852",
    "33853", "33857", "33859", "33860", "33865", "33867", "33868", "33870", "33872", "33873",
    "33875", "33876", "33880", "33881", "33884", "33888", "33890", "33896", "33897", "33898",
    "33901", "33903", "33905", "33907", "33908", "33912", "33913", "33916", "33917", "33919",
    "33920", "33922", "33928", "33931", "33931", "33935", "33936", "33946", "33947", "33950",
    "33955", "33956", "33957", "33960", "33965", "33966", "33967", "33967", "33971", "33972",
    "33973", "33974", "33976", "33980", "33982", "33983", "33993", "34102", "34103", "34104",
    "34105", "34108", "34109", "34110", "34112", "34113", "34114", "34116", "34117", "34119",
    "34120", "34134", "34134", "34135", "34135", "34141", "34142", "34145", "34201", "34202",
    "34203", "34205", "34207", "34208", "34209", "34210", "34211", "34212", "34215", "34217",
    "34219", "34221", "34222", "34223", "34224", "34228", "34229", "34231", "34232", "34233",
    "34234", "34235", "34236", "34237", "34238", "34239", "34240", "34241", "34242", "34243",
    "34249", "34251", "34266", "34269", "34275", "34285", "34286", "34287", "34291", "34292",
    "34293", "34420", "34428", "34429", "34431", "34432", "34433", "34434", "34436", "34442",
    "34446", "34446", "34448", "34448", "34449", "34450", "34452", "34453", "34461", "34470",
    "34471", "34472", "34473", "34474", "34475", "34476", "34479", "34480", "34481", "34482",
    "34484", "34488", "34491", "34498", "34601", "34602", "34604", "34606", "34607", "34608",
    "34609", "34610", "34613", "34614", "34637", "34638", "34639", "34652", "34653", "34654",
    "34655", "34667", "34668", "34669", "34677", "34683", "34684", "34685", "34688", "34689",
    "34690", "34691", "34695", "34698", "34705", "34711", "34714", "34715", "34715", "34731",
    "34734", "34736", "34737", "34737", "34739", "34741", "34743", "34744", "34746", "34747",
    "34748", "34753", "34756", "34758", "34759", "34761", "34762", "34769", "34771", "34772",
    "34773", "34785", "34786", "34787", "34787", "34788", "34797", "34797", "34945", "34946",
    "34947", "34949", "34950", "34951", "34952", "34952", "34953", "34953", "34956", "34957",
    "34972", "34974", "34981", "34982", "34983", "34983", "34984", "34984", "34986", "34986",
    "34987", "34987", "34990", "34994", "34996", "34997"
]

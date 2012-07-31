// JavaScript Document
var popup = false;

function ShowOnlyOnePopup(url,b,h) {
  var window_left = (screen.width-b)/2;
  var window_top = (screen.height-h)/2;
  if ( ( popup ) && !popup.closed ) {
    popup.location.href=url;  
  } else {
    popup=window.open(url,"ny","toolbar=no,copyhistory=no,location=no,left=" + window_left + ",top=" + window_top + ",directories=no,status=no,menubar=no,scrollbars=yes,resizable=no,width="+b+",height="+h);
  //  popup.closed = false;
  };
  if (!(navigator.appName == "Microsoft Internet Explorer" && parseInt(navigator.appVersion.substring(0,1)) <4))
        {popup.focus();}
} 

//This is to confirm deleting items
/*
Redirects the user to the delete-page, if they answer yes to delete the given tutor
*/
function deleteConfirm(strUrl, Name) {
	if (confirm("Vil du slette "+Name+"?")){
		location.href = strUrl;
	}
}




//Shows a popup-window.


function NewWindowVis(tutorid, myname, w, h, scroll) {
	url = "visTutor.php?tutorid="+tutorid;
	var winl = (screen.width - w) / 2;
	var wint = (screen.height - h) / 2;
	winprops = 'height='+h+',width='+w+',top='+wint+',left='+winl+',scrollbars='+scroll+',resizable'
	win = window.open(url, myname, winprops)
	if (parseInt(navigator.appVersion) >= 4) { win.window.focus(); }
}


function closeThePopup(strURL) {
  opener.location.href= strURL;
  //  opener.location.reload(true); 
  window.close();

}

/* This function can be used to close any popup no matter, whether it
is a GreyBox popup or normal popup
*/
function closeWindow(objThis) {
 	if (parent.parent.GB_CURRENT != null)
 		return parent.parent.GB_hide();
 	else
		return this.window.close();
}


/***
GreyBox related functions
***/

//GreyBox window, whichs reload on close

GB_ReloadOnCloseShow = function(caption, url, /* optional */ height, width, callback_fn) {
    var options = {
        caption: caption,
        height: height || 500,
        width: width || 500,
        fullscreen: false,
        show_loading: true,
        reload_on_close: true,
        callback_fn: callback_fn
    }
    var win = new GB_Window(options);
    return win.show(url);
}


function disableAndEnableFields(arrDisable, arrEnable) {
	for(i = 0; i < arrDisable.length; i++) {
//		alert(arrDisable[i]);		
		arrDisable[i].disabled = true;
		
 	}	
//	for(i = 0; i < arrEnable.length; i++) {
//      	arrEnable[i].disabled = false;
// 	}	
	arrEnable.disabled = false;

}

function disableAndEnableFieldsInStrings(arrDisable, arrEnable) {
	for(i = 0; i < arrDisable.length; i++) {
		objTmp = document.getElementById(arrDisable[i]);
		objTmp.disabled = true;
		
 	}	
	for(i = 0; i < arrEnable.length; i++) {
		objTmp = document.getElementById(arrEnable[i]);
      	objTmp.disabled = false;
 	}	
}

//
//This form submits the given form, if the event is equal to enter.

function submitenter(objForm,e)
{
  
	var keycode;	
	if (window.event) keycode = window.event.keyCode;
	else if (e) keycode = e.which;
	else return true;

	if (keycode == 13)
	   {
	   objForm.submit();
	   return false;
	   }
	else
	   return true;
}

bName= navigator.appName;
bVersion= parseFloat(navigator.appVersion);
var NS, IE;
NS = false;
IE = false;
if (bName== "Netscape" && bVersion >= 4) var NS = true
else if (bName== "Microsoft Internet Explorer" && bVersion >= 4) IE = true;
	
	
function moveSelected( strSourceID, strTargetID, strChanged )
{
  var objSource = document.getElementById( strSourceID );
  var objTarget = document.getElementById( strTargetID );
  var objChanged = document.getElementById( strChanged );
  /*nu ved PHP-scriptet at select-boksene er ændret, dvs. opdateringerne skal laves */
  objChanged.value = 'true';
  if( objSource.selectedIndex > -1 ) {
      var objOption = objSource.options[ objSource.selectedIndex ];
      var objNewOption = new Option( objOption.text, objOption.value )
	/* lidt browser specifikt
	 */
			
	if (IE) objTarget.add( objNewOption )
		  else if (NS) objTarget.add( objNewOption, null );
      objSource.remove( objSource.selectedIndex );
  }
}
	
function submitFormen(objForm, strSelect, strIEfix, strChangedObj) {
    var objChanged = document.getElementById(strChangedObj);
    //Der er ingen grund til at køre al koden igennem, hvis man ikke har ændret grupperne
    if (objChanged.value == '') return true;
    
    var objSelect = document.getElementById( strSelect );
    objSelect.multiple = true;
    //alert(objSelect.length);	
    //IE kan åbenbart ikke følge med, så vi skal lige have en lille pause ind. Og det skal desværre være en alert.
    if (IE) {
      alert("Dette skal lige indsættes for at IE vil vælge alle elementerne i select-boksene. Mozilla fungerer fint.");
    }
    
    for (var i=0;i<objSelect.length;i++) {
      objSelect[i].selected = true;
    }
    
  return true;
  
}

function setFormFieldFromSelect(objSelect, strFormField) {
  var objForm = document.getElementById( strFormField );
  objForm.value = objSelect.options[ objSelect.selectedIndex ].value;

}

//A function to set the current time in the format (DDMMYYhhmm) on a field
function setNow(strTextField) {
  var objTextField = document.getElementById( strTextField );
  var oD = new Date();
  var month = prependString("" + (oD.getMonth() + 1),2,0);
  var hours = prependString("" + oD.getHours(),2,0);
  var minutes = prependString("" + oD.getMinutes(),2,0);
  var strNow = "" + oD.getDate() + "-" + month + "-" + oD.getFullYear();
  strNow = strNow + " " + hours + ":" + minutes;
  
  objTextField.value = strNow;
}

function prependString(strText, length, strPrepend) {
  while(strText.length < length) {
    strText = strPrepend + strText;
  }
  return strText;

}



function editRow(arrData, arrConvert) {
  for(var i in arrData) {
    //A simple textfield
    if (arrConvert[i].type == 'text') {
      var objText = document.getElementById( arrConvert[i].formField );
      if (objText != null)
	      objText.value = arrData[i];
	}
    //For a select, we need to iterate throug the elements to select the right one
    else if(arrConvert[i].type == 'select') {
      var objSelect = document.getElementById( arrConvert[i].formField );
	  if (objSelect != null)
	      for(var j = 0;j < objSelect.length; j++) {
			if (objSelect.options[j].value == arrData[i]) {
			  objSelect.selectedIndex = j;
			  break;
			}
	      }
    }
    //En radio-button klares.
    else if(arrConvert[i].type == 'radio') {
      for (var j = 0; j < arrConvert[i].formField.length; j++) {
		var objRadio = document.getElementById( arrConvert[i].formField[j].formField );
	      if (objRadio != null) {
			objRadio.checked = false;
			if (arrConvert[i].formField[j].value == arrData[i]) {
	  		  objRadio.checked = true;
			}
		  }
      }

    }
    
  }
}

/**
* This function displays a div-block if its now visible, otherwise it gets collapsed
* It also updates the content of strAName to a plus or minus sign
*/
s = 0;
function expandCollapse(strDivName, strAName) {
	var objA = document.getElementById(strAName);
	objDiv = document.getElementById(strDivName);
	objDiv = objDiv.style;
	if (s == 0) {
		objDiv.display = 'none';
	    objDiv.visibility = 'hidden';
		s++;		
	}
	if (objDiv.visibility == 'hidden') {
		objA.innerHTML = "-";
		objDiv.visibility = 'visible';
		objDiv.display = 'block';
	} else {
		objA.innerHTML = "+";
		objDiv.display = 'none';
	    objDiv.visibility = 'hidden';
		
	}
}


/*Sætter en E-mailadresse sammen:
//Bliver kaldt med 4 parametre:
//Username: det før snabel-A
//Ulaengde: hvor mange tegn der skal fjernes, af starten af Username
//Domaene: Det efter snabel-A
//Dlaengde: hvor mange tegn der skal fjernes af starten af Demaene
*/
function lav_gyldig_email_adresse(username,ulaengde,domaene,dlaengde) {
  username = username.substring(ulaengde, username.length);
  domaene = domaene.substring(dlaengde,domaene.length);
  return username + '@' + domaene;
}
function lav_email_adresse(username,ulaengde,domaene,dlaengde) {
  void(location.href = "mailto:"+lav_gyldig_email_adresse(username,ulaengde,domaene,dlaengde));	
  //return "mailto:"+lav_gyldig_email_adresse(username,ulaengde,domaene,dlaengde);
}


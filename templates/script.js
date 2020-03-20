function switchScreen() {
	var form = document.getElementById("screenselect");
	document.querySelector("section.enabled").className = "";
	
	var screen = form.elements.screen.value;
	document.getElementById(screen).className = "enabled";
}
function paginate() {
	var sort = document.getElementById("sort").value;
	var perPage = Number(document.getElementById("perpage").value);
	var messages = document.getElementById("messages");
	
	var pageCount = Math.ceil(messages.children.length / perPage);
	document.getElementById("page").max = pageCount;
	document.getElementById("pagecount").innerText = pageCount;
	
	var page = Number(document.getElementById("page").value);
	if (page > pageCount) {
		page = pageCount;
		document.getElementById("page").value = pageCount;
	}
	window.scroll(0, 0);
	
	for (var i = 0; i < messages.children.length; i++)
		messages.children[i].removeAttribute("data-shown");
	
	if (perPage == 0) {
		for (var i = 0; i < messages.children.length; i++)
			messages.children[i].setAttribute("data-shown", "data-shown");
		
		document.getElementById("page").value = "1";
		document.getElementById("page").max = "1";
		document.getElementById("pagecount").innerText = "1";
		return;
	}
	
	var skippedElements = (page - 1) * perPage;
	if (sort == "desc")
		for (var i = 0; i < perPage; i++)
			messages.children[messages.children.length - skippedElements - 1 - i].setAttribute("data-shown", "data-shown");
	else 
		for (var i = 0; i < perPage; i++)
			messages.children[skippedElements + i].setAttribute("data-shown", "data-shown");
}
function showMessage(messageId) {
	var sort = document.getElementById("sort").value;
	var perPage = Number(document.getElementById("perpage").value);
	var messages = document.getElementById("messages");
	
	var message = document.querySelector("#overview [data-id=\"" + messageId + "\"]");
	
	if (sort == "desc")
		for (var i = 0; i < messages.children.length; i++) {
			if (messages.children[messages.children.length - 1 - i] == message) {
				var page = Math.floor(i / perPage) + 1;
				break;
			}
		}
	else
		for (var i = 0; i < messages.children.length; i++) {
			if (messages.children[i] == message) {
				var page = Math.floor(i / perPage) + 1;
				break;
			}
		}
		
	document.getElementById("page").value = page;
	paginate();
		
	var form = document.getElementById("screenselect");
	form.elements.screen.value = "overview";
	switchScreen();
	
	setTimeout(function() { message.scrollIntoView(); }, 100);
}

function sendAJAX() {
    let myRequest = new XMLHttpRequest();

    myRequest.open('GET', createUrl());
    myRequest.send();

    myRequest.onreadystatechange = function () {
        if (myRequest.readyState === 4) {
            let responseText = myRequest.responseText;
            let parser = new DOMParser();
            let xmlDoc = parser.parseFromString(responseText, "text/html");
            let container = xmlDoc.getElementById('my_table');
            let old_container = document.getElementById('my_table');
            old_container.parentNode.replaceChild(container, old_container);
        }
    };
}
function createUrl() {
    let url = '?';
    let selected_res = document.querySelector('input[name="resource"]:checked').value;
    switch (selected_res) {
        case 'dirs':  url += 'is_dir=true';break;
        case 'files': url += 'is_dir=false';break;
    }
    let accesses = document.querySelectorAll('input[name="access"]:checked');
    let acc_str = '';
    for (let i = 0; i < accesses.length; i++)
        acc_str += accesses[i].value + ',';

    if(accesses.length > 0)
        url += '&access_type=' + acc_str.substr(0, acc_str.length - 1);
    return url;
}


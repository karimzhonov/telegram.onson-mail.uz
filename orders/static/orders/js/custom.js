function scroll(element){
    const ele = document.getElementById(element);
    window.scrollTo(ele.offsetLeft,ele.offsetTop);
}

const search = new URLSearchParams(location.search)
document.querySelector("#number").value = search.get('number')
//    end owl carousel script 
function send() {
    event.preventDefault();
    const value = document.querySelector("#number").value
    location.href = `/?number=${value}`
    return false;
}


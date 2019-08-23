if (!window.dash_clientside) {
    window.dash_clientside = {};
}

// create the "ui" namespace within dash_clientside
window.dash_clientside.ui = { 
    // this function should be used in the callback whenever the table viewport has changed
    replaceWithLinks: function(trigger) {
        // find all dash-table cells that are in column 0
        let cells = document.getElementsByClassName("dash-cell column-2");
        re = /^http/;
        cells.forEach((elem, index, array) => {
            // each cell element should be modified with a new link
            // elem.children[0].innerText contains the link information, which we append to a specified route on our server
            //elem.children[0].innerHTML
            if (/^http/.test(elem.children[0].innerHTML)){
                elem.children[0].innerHTML =
                    "<a href='" +
                    elem.children[0].innerText +
                    "'> Link </a>";
            }
        });
        // arbitrary return.. callback needs a target
        return true;
    }
}
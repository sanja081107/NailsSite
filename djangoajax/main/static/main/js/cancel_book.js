function CancelBook(id) {

    var post = document.getElementById("post-"+id+"");
    $(".post").empty();

    var yes = document.createElement("a");
    var no = document.createElement("button");
    var quest = document.createElement("label");

    yes.innerHTML = "Да";
    yes.className = "btn delete-book-btn btn-outline-danger";
    yes.href = "/not_active_"+id+""

    no.innerHTML = "Нет";
    no.className = "btn delete-book-btn btn-outline-success";
    no.addEventListener("click", NoCancelBook, false);

    quest.innerHTML = "Вы уверены?&nbsp;&nbsp;";

    post.append(quest, yes, no);

//  alert("Вы уверены что хотите удалить запись: "+id)

};

function NoCancelBook() {

    $(".post").empty();

};

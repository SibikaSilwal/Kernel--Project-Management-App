function OpenProject(a_ProjectId) {
    window.location.href = "/project/" + a_ProjectId;
}
function OpenTodo(a_ProjectId) {
    window.location.href = "/todos/" + a_ProjectId;
}
function OpenFile(a_ProjectId){
    window.location.href = "/files/" + a_ProjectId;
}
function OpenDiscovery(a_ProjectId){
    window.location.href = "/"+a_ProjectId + "/discovery";
}
function MarkTaskComplete(a_checkboxId, a_taskId) {
    var taskCheckBox = document.getElementById(a_checkboxId);
    let checked;
    if(taskCheckBox.checked){
        checked =1;
        console.log("checked." )
    }else{
        checked =0;
        console.log("unchecked!" )
    }
    $.ajax({
        type: 'POST',
        url: "/markTaskDone",
        data: {done: checked, taskId: a_taskId},
        dataType: "text",
        success: function(data){
                  console.log("success! ", checked)
                 },
        
      });
}

$(function () {
  $('[data-toggle="popover"]').popover()
})


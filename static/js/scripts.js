function submit_form()
{
    // check the user provided all we need and send to the server
    var email = document.getelementbyid("email").value;
    if (!validate_email(email))
    {
        alert("You entered invalid email")
        return false;
    }
    var days = document.getElementById("days").value;
    if (days == "")
    {
        alert("You need to chose number of days")
        return false;
    }
    var node_count = document.getElementById("node_count").value;
    if (node_count == "")
    {
        alert("You need to chose number of individuals in the population")
        return false;
    }
    var social_edge_count = document.getElementById("social_edge_count").value;
    if (social_edge_count == "")
    {
        alert("You need to chose number of social connections")
        return false;
    }
    var epi_edge_count = document.getElementById("epi_edge_count").value;
    if (epi_edge_count == "")
    {
        alert("You need to chose number of epidemiological connections")
        return false;
    }
    // all valid - send form
    return true;
}

function validate_email(mail)
{
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(myForm.emailAddr.value))
    {
        return true;
    }
    return false;
}

function validate_file_upload(fileName)
{
    var allowed_extensions = new Array("csv");
    var file_extension = fileName.split('.').pop().toLowerCase(); // split function will split the filename by dot(.), and pop function will pop the last element from the array which will give you the extension as well. If there will be no extension then it will return the filename.
    for(var i = 0; i < allowed_extensions.length; i++)
    {
        if (allowed_extensions[i] == file_extension)
        {
            return true; // valid file extension
        }
    }
    return false;
}
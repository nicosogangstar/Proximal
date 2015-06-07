 function stream( position ){
	console.log(navigator.geolocation);
	console.log(position);
	if (navigator.geolocation) {
	    console.log("requesting");
		$.ajax({
			url:"view",
			"dataType":"json",
			data:{
				"longitude":1,
				"latitude": 1,
				"radius":1609,
				"page":0,
				"numpost":5
			},
			success:function( output ){
				console.log(output);
				//			    ___    ___   ___   _______
				//		       |   |  |   | |   | |   __  |
				//             |   |__|   | |   | |  |__| |
				//             |    __    | |   | |   ____|
				//		       |   |  |   | |   | |  |
				//		       |___|  |___| |___| |__|
				//
				//				             | |
				//		  		             | |
				//			  	             | |
				//			               \     /
				//				            \   /
				//append to #images	         \ /

				posts = output.posts;
				var htmlString='';
				var imageinfo='';
				for (var i = 0; i < posts.length; i++){
				  //template from stack overflow: 'data:image/png;base64,iVBORw0KGgoAAAANS'
					imageinfo = "data:image/png;base64,"+posts[i].image_data.replace("\\r\\n", "\r\n");
				  	htmlString+='<div class="package"><img class="money" src="'+imageinfo+'" />';
          			//htmlString+='<div class="popularity"><a><div class="up"><img class="arrow" src="blue.png" /></div></a><a><div class="down"><img class="arrow" src="red.png" /></div></a></div>';
          			htmlString+='<div class="subtitle">'+posts[i].caption+'</div></div>';
				}
				//console.log(htmlString);
				$("#images").append(htmlString);
			},
			error:function( err ){
				console.log(err);
			}
		});
	}else{
		console.log("browser not supported. newbz get rekt")
	}
}

$(document).ready(function(){
	navigator.geolocation.getCurrentPosition(stream);
});

$("button").click(function(){
	navigator.geolocation.getCurrentPosition(stream);
});
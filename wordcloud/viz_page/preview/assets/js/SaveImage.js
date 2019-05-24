function saveImage(format, orcid)
{
	var canvas = document.createElement("canvas")
	canvas.id = 'wordcloud-canvas'
    var parser = new DOMParser()
 
       
    httpGetAsync("http://localhost:8081/" + orcid, function(resp)
    {
        var svg = parser.parseFromString(resp, 'image/svg+xml')['childNodes'][0] //svg itself
        CanvasFromSVG(svg, canvas, format) //convert svg attributes to canvas
        saveAsImage(format)
    })
    
    //get data from server
    function httpGetAsync(theUrl, callback)
    {
        var xmlHttp = new XMLHttpRequest()
        xmlHttp.onreadystatechange = function() 
        { 
            if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
                callback(xmlHttp.responseText)
        }
        xmlHttp.open("GET", theUrl, true) // true for asynchronous 
        xmlHttp.send(null)
    }

    //save image as jpeg/png
	function saveAsImage(format)// requires FileSaver.js
	{
		canvas.toBlob(function(blob)
		{
			saveAs(blob, orcid + '.' + format)
		}, 'image/' + format, 1)
		
	}
    
    //parse svg attributes and convert them to canvas
	function CanvasFromSVG(svg, canvas, format)
	{
		var svgText = svg.childNodes[0].childNodes //select children of <g>

		canvas.width = svg.width.baseVal.value  //copy svg width/height to canvas
		canvas.height = svg.height.baseVal.value
		
		if (format == 'jpeg')
		{
			//if jpg than render as without transparent background
			var ctx = canvas.getContext("2d", {alpha:false})
			ctx.clearRect(0,0, canvas.width, canvas.height)
			ctx.fillStyle = '#FFFFFF'
			ctx.fillRect(0,0, canvas.width, canvas.height)
		}
		else
		{
			var ctx = canvas.getContext("2d")
		}
		
		svgText.forEach(function(el)
		{
			//remap all the svg attributes to canvas
			var attr = svgElementParse(el)
			ctx.font = attr['font-size'] + ' ' + attr['font-family']
			ctx.fillStyle = attr['fill']
			ctx.strokeStyle = attr['stroke']
			ctx.lineWidth = 0.2
			ctx.textAlign = 'center' // better not touch
			ctx.fillText(attr['text'], attr['transform'][0], attr['transform'][1])
			ctx.strokeText(attr['text'], attr['transform'][0], attr['transform'][1])
		})

		function svgElementParse(svg)
		{
			var attributes = svg.attributes 
			var style = attributes.style.value.split(';') //split string of attributes into array 
			var styleArr = []
			style.forEach(function(el) //split array elements into arrays by ":"
			{
				if (el != "")
				styleArr.push(el.trim().split(':'))
			})
			
			var dict = {}
			styleArr.forEach(function(el) //transform array of arrays into dictionary
			{
				dict[el[0]] = el[1].trim()
			})
			dict['transform'] = attributes.transform.value.match(/\((\d+),(\d+)\)/).slice(1) //regex because transform=translate(d,d)
			dict['text-anchor'] = attributes['text-anchor'].value
			dict['text'] = svg.textContent
			
			return dict
		}
	}
}
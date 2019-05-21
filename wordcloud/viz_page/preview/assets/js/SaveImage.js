
function saveImage(format, svgId)
{
	var prevCanv = document.getElementById('wordcloud-canvas')
	if (prevCanv != null){ prevCanv.remove() }
	
	var canvas = document.createElement("canvas")
	canvas.id = 'wordcloud-canvas'
	CanvasFromSVG(svgId, canvas, format)
	saveAsImage(format)
	
	
	function saveAsImage(format)// requires FileSaver.js
	{
		canvas.toBlob(function(blob)
		{
			saveAs(blob, 'image.' + format)
		}, 'image/' + format, 1)
		
	}

	function CanvasFromSVG(svgId, canvas, format)
	{
		var svg = document.getElementById(svgId) //get svg data
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
uniform float osg_FrameTime;  // in seconds
uniform bool flowTo;
uniform vec4 flowToColor;
uniform float flowToSpacing;
uniform float flowToSpeed;
uniform float flowToSpread;
uniform bool flowFrom;
uniform vec4 flowFromColor;
uniform float flowFromSpacing;
uniform float flowFromSpeed;
uniform float flowFromSpread;
uniform bool hasTexture;
uniform sampler2D textureUnit;
uniform float textureScale;
varying vec3 normal, lightDir, halfVector;

void main()
{
	vec3  dl = gl_LightSource[0].diffuse .rgb * gl_FrontMaterial.diffuse.rgb;
	vec3  al = gl_LightSource[0].ambient .rgb * gl_FrontMaterial.ambient.rgb + gl_FrontMaterial.emission.rgb;
	vec3  sl = gl_LightSource[0].specular.rgb * gl_FrontMaterial.specular.rgb;
	vec3  tx = (hasTexture ? texture2D ( textureUnit, gl_TexCoord[0].st ).rgb : vec3(1.0, 1.0, 1.0));
	float sh = gl_FrontMaterial.shininess;
	vec3 d, s;
	if (normal[0] == 0.0 && normal[1] == 0.0 && normal[2] == 0.0)
	{
	  d = tx * (dl * vec3(0.5, 0.5, 0.5) + al);
	  s = vec3(0.0, 0.0, 0.0);
	}
	else
	{
	  d = tx * ( dl * max ( dot ( normal, lightDir   ), 0.0 ) + al );
	  s = sl *  pow ( max ( dot ( normal, halfVector ), 0.0 ), sh );
	}
	vec4 baseColor = vec4 ( min ( d + s, 1.0) , 1.0 );
	
	float texCoord = gl_TexCoord[0].t * textureScale;
	
	float glowTo = 0.0;
	if (flowTo)
	{
	  float peakGlow = mod(osg_FrameTime, flowToSpacing / flowToSpeed) * flowToSpeed;
	  float glowWidth = flowToSpacing * flowToSpread;
	  float distanceFromPeakGlow = peakGlow - mod(texCoord, flowToSpacing);
	  if (distanceFromPeakGlow < 0.0)
		  distanceFromPeakGlow += flowToSpacing;
	  if (distanceFromPeakGlow < glowWidth)
		  glowTo = 1.0 - distanceFromPeakGlow / glowWidth;
	}
	
	float glowFrom = 0.0;
	if (flowFrom)
	{
	  float period = flowFromSpacing / flowFromSpeed;
	  float peakGlow = (1.0 - mod(osg_FrameTime, period) / period) * flowFromSpacing;
	  float glowWidth = flowFromSpacing * flowFromSpread;
	  float distanceFromPeakGlow = mod(texCoord, flowFromSpacing) - peakGlow;
	  if (distanceFromPeakGlow < 0.0)
		  distanceFromPeakGlow += flowFromSpacing;
	  if (distanceFromPeakGlow < glowWidth)
		  glowFrom = 1.0 - distanceFromPeakGlow / glowWidth;
	}
	
	vec4  glowColor = vec4(max(flowToColor[0] * glowTo, flowFromColor[0] * glowFrom), 
						 max(flowToColor[1] * glowTo, flowFromColor[1] * glowFrom), 
						 max(flowToColor[2] * glowTo, flowFromColor[2] * glowFrom), 
						 1.0);
	float glow = max(flowToColor[3] * glowTo, flowFromColor[3] * glowFrom);
	
	gl_FragColor = vec4(glowColor * glow + baseColor * (1.0 - glow));
}

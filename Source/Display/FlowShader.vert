varying vec3 normal, lightDir, halfVector;

void main()
{
	gl_TexCoord[0] = gl_TextureMatrix[0] * gl_MultiTexCoord0;
	if (gl_Normal[0] == 0.0 && gl_Normal[1] == 0.0 && gl_Normal[2] == 0.0)
		normal     = gl_Normal;
	else
		normal     = normalize ( gl_NormalMatrix * gl_Normal ) ;
	lightDir   = normalize ( gl_LightSource[0].position.xyz ) ;
	halfVector = normalize ( gl_LightSource[0].halfVector.xyz ) ;
	gl_Position = ftransform () ;
}
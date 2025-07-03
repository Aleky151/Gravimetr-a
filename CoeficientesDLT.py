import numpy as np

def obtenerCoefDLT(coord_imagen, coord_terrestre):
    A=[]
    for (x,y),(X,Y,Z) in zip(coord_imagen, coord_terrestre):
        A.append([X, Y, Z, 1, 0, 0, 0, 0, -x*X, -x*Y, -x*Z, -x])
        A.append([0, 0, 0, 0, X, Y, Z, 1, -y*X, -y*Y, -y*Z, -y])
    A=np.array(A)
    # Resolver para c0 a c10 (último vector singular)
    vh=np.linalg.svd(A)
    c=vh[-1, :] # Coeficientes c0 a c10
    return c
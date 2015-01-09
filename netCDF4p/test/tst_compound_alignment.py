""" This illustrates a bug when a structured array is extracted from a netCDF4.Variable using the slicing operation. 

Bug is observed with EPD 7.3-1 and 7.3-2 (64-bit)
"""
import netCDF4p as netCDF4
import numpy, tempfile, sys, os, unittest
from numpy.testing import assert_array_equal, assert_array_almost_equal

def string_to_bytes(xstring, size=-1, pad="\0"):
    nbytes = len(xstring)
    if (size >= 0):
        xsize = size
    else:
        xsize = nbytes
    xbytes = numpy.empty(xsize, dtype=numpy.uint8)
    xbytes[:] = ord(pad)
    if (nbytes > xsize):
        nbytes = xsize
    for i in range(nbytes):
        xbytes[i] = ord(xstring[i])
    return xbytes

cells     = numpy.array([ (387, 289, 65.64321899414062, -167.90093994140625, 3555, -10158, 8934, -16608, 19, 34199, 2, 0, 218, 619, 534, 314, 234, 65528, 39, 1524, 2429, 3137, 2795, 3092, 6431, 12949, 6780, 18099, 8248, 9331, 972, 553, 721, 2874, 2488, 3087, 3072, 2537, 3295, 334, 334, 9888, 10552, 7175, 6981, 7250, 8133, 14349, 16565, 17097, 20945, 13, 5, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 5, 3, 7, 0, 0, 10, 11, 15, 7, 14, 4, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 0, 6, 0, 12210, 16433, 45, 241, 243, 71, 131, [87, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (387, 290, 65.64067077636719, -167.93258666992188, 3546, -10161, 8934, -16611, 13, 34165, 1, 0, 215, 582, 534, 317, 204, 65528, 34, 1533, 2428, 3161, 2803, 3107, 6336, 12721, 6670, 17775, 7973, 8770, 933, 554, 714, 2904, 2480, 3102, 3087, 2560, 3323, 359, 359, 9934, 10585, 7235, 7007, 7315, 8209, 14421, 16538, 17046, 20924, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 5, 3, 7, 0, 0, 11, 11, 15, 6, 15, 3, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 0, 6, 0, 12235, 16433, 45, 241, 243, 71, 131, [-43, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (388, 287, 65.65902709960938, -167.84213256835938, 3574, -10167, 8936, -16602, 15, 34269, 1, 0, 213, 626, 521, 313, 230, 64, 35, 1519, 2391, 3091, 2719, 3011, 6313, 12685, 6657, 17785, 8169, 9420, 960, 541, 705, 2881, 2488, 3084, 3065, 2500, 3328, 357, 357, 10023, 10578, 7250, 6986, 7285, 8149, 14469, 16671, 17188, 20849, 13, 4, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 5, 3, 7, 0, 0, 11, 12, 15, 6, 15, 4, 4, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 12241, 16432, 25, 241, 243, 71, 131, [-41, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (388, 288, 65.65646362304688, -167.8740692138672, 3565, -10171, 8936, -16605, 17, 34234, 1, 0, 214, 618, 523, 310, 226, 70, 36, 1528, 2408, 3107, 2751, 3026, 6320, 12708, 6673, 17824, 8138, 9309, 960, 541, 712, 2881, 2496, 3084, 3079, 2477, 3259, 349, 349, 10023, 10528, 7281, 7011, 7285, 8149, 14416, 16503, 17057, 20928, 13, 5, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 5, 3, 7, 0, 0, 11, 12, 15, 6, 13, 4, 4, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 12239, 16433, 45, 241, 243, 71, 131, [-43, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (388, 289, 65.65390014648438, -167.9058380126953, 3555, -10174, 8935, -16608, 15, 34200, 2, 0, 212, 582, 526, 307, 208, 60, 40, 1519, 2408, 3107, 2751, 3042, 6226, 12504, 6548, 17477, 7880, 8732, 929, 541, 689, 2911, 2496, 3129, 3094, 2500, 3300, 342, 342, 10001, 10595, 7413, 7086, 7396, 8292, 14486, 16601, 16949, 21066, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 5, 3, 7, 0, 0, 11, 12, 15, 5, 13, 3, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 12272, 16433, 45, 241, 243, 71, 131, [83, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (388, 290, 65.6513442993164, -167.9374542236328, 3546, -10177, 8935, -16611, 6, 34166, 2, 0, 213, 568, 531, 315, 198, 64, 34, 1537, 2424, 3147, 2782, 3081, 6242, 12534, 6571, 17524, 7833, 8550, 921, 541, 689, 2926, 2496, 3144, 3102, 2546, 3341, 358, 358, 10045, 10629, 7421, 7078, 7448, 8326, 14485, 16572, 16984, 21085, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 5, 3, 7, 0, 0, 11, 12, 15, 5, 13, 3, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 12307, 16433, 45, 241, 243, 71, 131, [83, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (388, 291, 65.6487808227539, -167.96910095214844, 3536, -10180, 8934, -16614, 5, 34131, 1, 0, 218, 586, 538, 321, 211, 74, 40, 1546, 2424, 3171, 2806, 3113, 6368, 12821, 6704, 17895, 8029, 8835, 937, 549, 705, 2926, 2496, 3152, 3117, 2476, 3286, 350, 350, 9978, 10612, 7468, 7128, 7474, 8360, 14547, 16572, 17019, 20766, 13, 5, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 5, 3, 7, 0, 0, 11, 12, 15, 5, 13, 3, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (389, 287, 65.66973876953125, -167.84698486328125, 3574, -10183, 8937, -16603, 8, 34270, 2, 0, 211, 598, 526, 304, 206, 65528, 35, 1516, 2378, 3069, 2697, 2984, 6168, 12394, 6515, 17382, 7931, 9011, 935, 530, 694, 2923, 2495, 3147, 3106, 2530, 3413, 334, 334, 9999, 10723, 7479, 7160, 7494, 8378, 14631, 16670, 17111, 21141, 12, 6, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 6, 3, 7, 0, 0, 11, 13, 15, 6, 11, 3, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 3, 0, 6, 0, 12325, 16433, 45, 241, 243, 71, 131, [83, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (389, 288, 65.66716003417969, -167.87890625, 3565, -10186, 8937, -16606, 9, 34235, 2, 0, 212, 602, 528, 309, 218, 65528, 38, 1525, 2387, 3101, 2736, 3016, 6240, 12542, 6585, 17587, 7994, 9050, 943, 530, 701, 2938, 2503, 3170, 3128, 2552, 3371, 333, 333, 9930, 10706, 7533, 7176, 7546, 8412, 14595, 16697, 17010, 20876, 12, 6, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 6, 3, 7, 0, 0, 11, 13, 15, 6, 10, 3, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 3, 0, 6, 0, 12360, 16433, 45, 241, 243, 71, 131, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (389, 289, 65.66458892822266, -167.91065979003906, 3555, -10190, 8936, -16609, 5, 34201, 2, 0, 212, 561, 527, 311, 202, 65528, 34, 1524, 2412, 3117, 2744, 3032, 6137, 12342, 6461, 17241, 7721, 8408, 897, 530, 678, 2967, 2495, 3185, 3158, 2552, 3344, 335, 335, 9953, 10757, 7586, 7219, 7598, 8474, 14622, 16711, 17085, 20855, 12, 7, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 6, 3, 7, 0, 0, 12, 13, 15, 6, 11, 3, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 3, 0, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (389, 290, 65.6620101928711, -167.94241333007812, 3546, -10193, 8936, -16611, 5, 34166, 2, 0, 213, 558, 533, 315, 190, 65528, 35, 1533, 2420, 3141, 2767, 3071, 6168, 12424, 6500, 17312, 7721, 8360, 905, 530, 678, 2952, 2495, 3177, 3128, 2507, 3371, 334, 334, 9975, 10689, 7517, 7176, 7546, 8426, 14577, 16559, 17109, 21037, 12, 7, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 6, 3, 7, 0, 0, 12, 13, 15, 6, 11, 3, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 3, 0, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (389, 291, 65.65943145751953, -167.97409057617188, 3536, -10196, 8935, -16614, 5, 34132, 0, 0, 217, 578, 536, 324, 206, 65528, 36, 1542, 2420, 3165, 2799, 3095, 6303, 12683, 6640, 17713, 7924, 8654, 920, 546, 694, 2938, 2495, 3170, 3143, 2530, 3358, 327, 327, 9952, 10672, 7517, 7184, 7539, 8419, 14550, 16627, 17046, 20934, 12, 7, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 6, 3, 7, 0, 0, 11, 12, 15, 6, 11, 3, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 3, 0, 6, 0, 0, 3, 0, 0, 0, 255, 255, [23, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (389, 292, 65.65685272216797, -168.0056915283203, 3527, -10199, 8934, -16617, 5, 34097, 1, 0, 226, 625, 545, 329, 232, 65528, 56, 1542, 2428, 3189, 2845, 3165, 6580, 13244, 6943, 18555, 8375, 9328, 973, 569, 732, 2952, 2503, 3155, 3106, 2507, 3289, 341, 341, 9861, 10552, 7494, 7176, 7513, 8405, 14460, 16489, 16983, 20873, 11, 5, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 6, 3, 7, 0, 0, 10, 11, 15, 6, 10, 3, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 3, 0, 6, 0, 0, 2, 0, 0, 0, 255, 255, [81, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (390, 287, 65.66167449951172, -167.85145568847656, 3573, -10045, 8937, -16603, 14, 34267, 1, 0, 213, 624, 529, 315, 216, 68, 44, 1533, 2414, 3105, 2719, 3022, 6294, 12637, 6630, 17704, 8134, 9315, 969, 542, 712, 2888, 2500, 3097, 3042, 2456, 3268, 334, 334, 10122, 10624, 7274, 7110, 7307, 8181, 14498, 16617, 17137, 21090, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 11, 13, 15, 5, 9, 3, 3, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 12243, 16433, 45, 241, 243, 71, 131, [-41, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (390, 288, 65.65919494628906, -167.88340759277344, 3564, -10048, 8936, -16606, 15, 34233, 2, 0, 215, 610, 526, 316, 213, 72, 38, 1533, 2414, 3105, 2735, 3038, 6278, 12621, 6607, 17641, 8055, 9125, 954, 542, 704, 2910, 2506, 3113, 3071, 2501, 3254, 342, 342, 10032, 10624, 7358, 7181, 7353, 8243, 14453, 16522, 17075, 20905, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 11, 13, 15, 5, 8, 3, 3, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 12255, 16433, 45, 241, 243, 71, 131, [83, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (390, 289, 65.65672302246094, -167.91519165039062, 3554, -10050, 8935, -16608, 10, 34198, 2, 0, 211, 570, 533, 318, 196, 64, 34, 1524, 2414, 3128, 2751, 3038, 6177, 12399, 6491, 17304, 7774, 8523, 914, 542, 688, 2940, 2500, 3143, 3086, 2523, 3310, 335, 335, 10054, 10691, 7456, 7199, 7470, 8347, 14560, 16656, 17000, 20986, 13, 7, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 13, 15, 5, 9, 3, 3, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 12318, 16433, 45, 241, 243, 71, 131, [83, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (390, 290, 65.65425109863281, -167.9468994140625, 3545, -10053, 8935, -16611, 5, 34164, 2, 0, 213, 572, 538, 319, 196, 64, 41, 1533, 2438, 3160, 2789, 3077, 6231, 12534, 6561, 17477, 7829, 8538, 922, 542, 696, 2933, 2500, 3151, 3086, 2456, 3324, 343, 343, 10054, 10674, 7441, 7199, 7470, 8340, 14533, 16562, 16987, 20985, 13, 7, 6, 15, 15, 15, 15, 0, 9, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 13, 15, 5, 9, 3, 3, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (390, 291, 65.65176391601562, -167.97862243652344, 3535, -10056, 8934, -16614, 5, 34129, 2, 0, 220, 600, 544, 324, 209, 78, 52, 1532, 2446, 3175, 2821, 3124, 6426, 12898, 6754, 18017, 8110, 8951, 961, 557, 712, 2948, 2500, 3143, 3094, 2456, 3268, 342, 342, 10054, 10624, 7433, 7181, 7490, 8361, 14524, 16615, 17011, 21005, 13, 6, 6, 15, 15, 15, 15, 0, 9, 5, 8, 8, 4, 5, 4, 7, 0, 0, 11, 12, 15, 5, 9, 3, 3, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (391, 286, 65.67485809326172, -167.82440185546875, 3583, -10058, 8938, -16600, 13, 34302, 2, 0, 209, 603, 516, 306, 206, 69, 42, 1500, 2373, 3048, 2663, 2961, 6145, 12346, 6479, 17279, 7924, 9049, 930, 526, 697, 2902, 2500, 3127, 3090, 2513, 3361, 338, 338, 10063, 10809, 7433, 7131, 7427, 8311, 14635, 16809, 17275, 20874, 13, 5, 7, 15, 15, 15, 15, 0, 10, 6, 8, 8, 4, 5, 4, 7, 0, 0, 11, 13, 15, 6, 12, 3, 2, 5, 3, 15, 15, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 12294, 16433, 45, 241, 243, 72, 131, [85, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (391, 287, 65.67237854003906, -167.8563232421875, 3573, -10061, 8938, -16603, 7, 34268, 2, 0, 212, 608, 525, 309, 220, 66, 42, 1517, 2389, 3080, 2701, 2985, 6200, 12440, 6557, 17474, 7995, 9121, 946, 534, 697, 2932, 2500, 3165, 3113, 2490, 3320, 329, 329, 10085, 10776, 7527, 7186, 7538, 8414, 14652, 16698, 17108, 20833, 13, 5, 7, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 11, 13, 15, 6, 12, 3, 2, 5, 3, 15, 15, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 12350, 16433, 45, 241, 243, 71, 131, [83, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (391, 288, 65.66989135742188, -167.8882598876953, 3564, -10064, 8937, -16606, 6, 34233, 2, 0, 213, 598, 528, 311, 225, 77, 39, 1534, 2405, 3111, 2724, 3016, 6239, 12527, 6572, 17545, 7971, 8954, 946, 542, 704, 2955, 2507, 3172, 3128, 2467, 3320, 353, 353, 9952, 10725, 7534, 7241, 7571, 8441, 14617, 16615, 17081, 20772, 13, 5, 7, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 11, 13, 15, 6, 11, 3, 2, 5, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 12369, 16433, 45, 241, 243, 71, 131, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (391, 289, 65.66740417480469, -167.9201202392578, 3554, -10066, 8936, -16609, 5, 34198, 2, 0, 209, 552, 534, 314, 188, 62, 40, 1525, 2413, 3119, 2740, 3032, 6114, 12267, 6409, 17084, 7635, 8240, 891, 534, 681, 2940, 2500, 3180, 3135, 2536, 3333, 330, 330, 10018, 10775, 7597, 7214, 7610, 8476, 14660, 16683, 17158, 20892, 13, 7, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 13, 15, 6, 12, 3, 2, 5, 3, 15, 15, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (391, 290, 65.66490936279297, -167.951904296875, 3545, -10069, 8936, -16612, 5, 34164, 2, 0, 212, 560, 530, 319, 192, 61, 38, 1525, 2421, 3143, 2763, 3055, 6184, 12425, 6502, 17326, 7729, 8391, 907, 542, 697, 2962, 2500, 3157, 3135, 2490, 3306, 330, 330, 9952, 10758, 7542, 7214, 7564, 8441, 14582, 16669, 17132, 20831, 13, 7, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 13, 15, 5, 12, 3, 2, 5, 3, 15, 15, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (391, 291, 65.66241455078125, -167.98362731933594, 3535, -10072, 8935, -16615, 5, 34129, 0, 0, 219, 586, 545, 320, 207, 70, 47, 1543, 2438, 3166, 2802, 3110, 6357, 12780, 6697, 17880, 8011, 8788, 938, 557, 704, 2962, 2500, 3172, 3128, 2490, 3319, 353, 353, 10018, 10691, 7542, 7186, 7557, 8441, 14590, 16614, 17131, 20971, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 11, 12, 15, 5, 12, 3, 2, 5, 3, 15, 15, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 0, 3, 0, 0, 0, 255, 255, [23, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (391, 292, 65.65991973876953, -168.01527404785156, 3526, -10075, 8935, -16618, 5, 34095, 0, 0, 228, 635, 548, 330, 234, 91, 63, 1542, 2446, 3198, 2848, 3165, 6639, 13364, 6985, 18685, 8480, 9494, 993, 573, 744, 2947, 2500, 3165, 3113, 2467, 3250, 353, 353, 9929, 10606, 7518, 7204, 7531, 8407, 14461, 16475, 16938, 20849, 13, 4, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 10, 11, 15, 6, 12, 3, 2, 5, 4, 15, 15, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 0, 3, 0, 0, 0, 255, 255, [23, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (392, 286, 65.68557739257812, -167.8292694091797, 3583, -10074, 8939, -16601, 6, 34303, 2, 0, 205, 586, 519, 302, 195, 65528, 36, 1511, 2365, 3033, 2638, 2931, 6076, 12187, 6396, 17037, 7800, 8827, 916, 521, 675, 2950, 2505, 3202, 3155, 2456, 3417, 343, 343, 9789, 10958, 7655, 7207, 7655, 8550, 14842, 16863, 17290, 20901, 13, 5, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 13, 15, 5, 11, 2, 2, 6, 3, 15, 15, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 0, 6, 0, 12393, 16433, 45, 241, 243, 72, 131, [83, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (392, 287, 65.6830825805664, -167.8612823486328, 3573, -10077, 8939, -16604, 5, 34268, 2, 0, 211, 609, 527, 308, 217, 65528, 38, 1519, 2399, 3073, 2700, 2994, 6226, 12518, 6568, 17499, 8037, 9190, 948, 529, 699, 2957, 2497, 3195, 3140, 2525, 3362, 342, 342, 9765, 10857, 7609, 7207, 7635, 8508, 14686, 16766, 17165, 20820, 13, 5, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 11, 13, 15, 5, 12, 2, 3, 6, 3, 15, 15, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 0, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (392, 288, 65.68058013916016, -167.8932342529297, 3564, -10079, 8938, -16606, 5, 34233, 2, 0, 209, 575, 527, 312, 206, 65528, 29, 1528, 2407, 3105, 2716, 3002, 6163, 12369, 6474, 17264, 7808, 8653, 908, 537, 691, 2950, 2497, 3187, 3132, 2502, 3361, 351, 351, 9601, 10724, 7571, 7188, 7596, 8460, 14572, 16655, 17127, 20820, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 13, 15, 5, 12, 2, 3, 6, 3, 15, 15, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 0, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (392, 289, 65.6780776977539, -167.92510986328125, 3554, -10082, 8937, -16609, 5, 34198, 2, 0, 208, 538, 531, 314, 182, 65528, 37, 1519, 2415, 3105, 2732, 3017, 6061, 12148, 6357, 16927, 7539, 8101, 885, 529, 675, 2957, 2505, 3195, 3147, 2502, 3334, 352, 352, 9624, 10740, 7609, 7151, 7609, 8487, 14624, 16737, 17089, 20859, 13, 7, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 13, 15, 5, 11, 2, 3, 6, 3, 15, 15, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 0, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (392, 290, 65.67557525634766, -167.9569091796875, 3545, -10085, 8937, -16612, 5, 34163, 0, 0, 212, 550, 530, 320, 185, 65528, 43, 1528, 2423, 3136, 2755, 3056, 6147, 12345, 6459, 17225, 7673, 8283, 885, 529, 683, 2965, 2497, 3195, 3147, 2479, 3334, 344, 344, 9600, 10774, 7608, 7179, 7628, 8508, 14659, 16737, 17113, 20818, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 13, 15, 5, 12, 2, 3, 6, 3, 15, 15, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 0, 6, 0, 0, 3, 0, 0, 0, 255, 255, [23, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (392, 291, 65.67306518554688, -167.9886474609375, 3535, -10088, 8936, -16615, 5, 34129, 0, 0, 214, 574, 533, 322, 199, 65528, 49, 1527, 2423, 3160, 2786, 3088, 6297, 12668, 6623, 17664, 7910, 8630, 924, 545, 699, 2972, 2505, 3187, 3139, 2525, 3334, 351, 351, 9647, 10757, 7601, 7169, 7622, 8494, 14633, 16709, 17113, 21018, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 8, 7, 4, 5, 4, 7, 0, 0, 11, 12, 15, 5, 11, 2, 3, 6, 3, 15, 15, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 0, 6, 0, 0, 3, 0, 0, 0, 255, 255, [23, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (392, 292, 65.67056274414062, -168.02029418945312, 3526, -10091, 8936, -16618, 5, 34095, 2, 0, 225, 627, 539, 327, 220, 65528, 56, 1527, 2431, 3176, 2833, 3150, 6604, 13291, 6951, 18566, 8416, 9411, 979, 568, 738, 2965, 2497, 3187, 3139, 2479, 3292, 350, 350, 9624, 10723, 7585, 7197, 7615, 8487, 14606, 16571, 17037, 20836, 13, 4, 6, 15, 15, 15, 15, 0, 10, 5, 7, 7, 4, 5, 4, 7, 0, 0, 10, 11, 15, 5, 12, 2, 3, 6, 3, 15, 15, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 0, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (393, 286, 65.6962890625, -167.834228515625, 3583, -10089, 8940, -16601, 5, 34303, 1, 0, 203, 586, 515, 301, 208, 62, 39, 1504, 2362, 3033, 2647, 2933, 6076, 12190, 6396, 17048, 7825, 8887, 931, 518, 673, 2985, 2506, 3242, 3177, 2499, 3353, 341, 341, 10146, 11031, 7764, 7255, 7766, 8653, 14901, 16912, 17203, 21074, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 11, 14, 15, 5, 9, 2, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (393, 287, 65.69377899169922, -167.8662567138672, 3573, -10092, 8939, -16604, 5, 34268, 0, 0, 205, 592, 521, 303, 211, 61, 38, 1503, 2387, 3057, 2671, 2956, 6139, 12323, 6467, 17236, 7873, 8958, 931, 525, 681, 3000, 2499, 3235, 3185, 2476, 3339, 333, 333, 10101, 11014, 7749, 7264, 7779, 8674, 14910, 16840, 17229, 20975, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 11, 14, 15, 5, 10, 2, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 0, 3, 0, 0, 0, 255, 255, [23, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (393, 288, 65.6912612915039, -167.89822387695312, 3564, -10095, 8939, -16607, 5, 34233, 0, 0, 204, 542, 529, 304, 189, 59, 35, 1512, 2403, 3081, 2702, 2987, 6013, 12080, 6318, 16828, 7540, 8173, 892, 518, 666, 2978, 2499, 3227, 3163, 2476, 3353, 350, 350, 9966, 10849, 7679, 7236, 7707, 8585, 14724, 16670, 17097, 21013, 13, 7, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 14, 15, 5, 10, 2, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 0, 3, 0, 0, 0, 255, 255, [23, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (393, 289, 65.68875122070312, -167.93011474609375, 3554, -10098, 8938, -16610, 5, 34198, 2, 0, 203, 531, 529, 305, 169, 58, 35, 1521, 2403, 3097, 2726, 3003, 6013, 12064, 6310, 16812, 7460, 7990, 876, 525, 658, 2985, 2499, 3227, 3155, 2499, 3339, 343, 343, 9988, 10799, 7664, 7199, 7680, 8564, 14671, 16726, 17136, 21032, 13, 8, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 14, 15, 5, 10, 2, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (393, 290, 65.68623352050781, -167.9619140625, 3545, -10101, 8938, -16613, 5, 34163, 2, 0, 206, 546, 529, 311, 188, 64, 43, 1520, 2411, 3120, 2741, 3050, 6115, 12300, 6436, 17158, 7643, 8228, 900, 533, 673, 2985, 2506, 3227, 3148, 2453, 3339, 342, 342, 10011, 10832, 7679, 7255, 7680, 8585, 14724, 16698, 17162, 20953, 13, 7, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 13, 15, 5, 9, 2, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (393, 291, 65.6837158203125, -167.99365234375, 3535, -10104, 8937, -16616, 5, 34129, 2, 0, 211, 567, 536, 318, 199, 70, 45, 1520, 2420, 3128, 2773, 3074, 6265, 12590, 6585, 17559, 7850, 8530, 923, 549, 689, 3000, 2499, 3242, 3140, 2499, 3325, 342, 342, 9988, 10782, 7664, 7217, 7674, 8557, 14635, 16655, 17083, 20893, 13, 7, 6, 15, 15, 15, 15, 0, 10, 5, 7, 7, 4, 5, 4, 7, 0, 0, 11, 13, 15, 5, 10, 2, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 0, 2, 0, 0, 0, 255, 255, [81, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (393, 292, 65.68119812011719, -168.0253143310547, 3526, -10107, 8937, -16619, 5, 34095, 2, 0, 221, 628, 535, 324, 219, 78, 51, 1529, 2419, 3152, 2804, 3128, 6573, 13234, 6930, 18526, 8430, 9490, 986, 557, 728, 3007, 2491, 3242, 3170, 2453, 3339, 357, 357, 9988, 10832, 7702, 7245, 7713, 8605, 14688, 16711, 17161, 20951, 13, 5, 6, 15, 15, 15, 15, 0, 10, 5, 7, 7, 4, 5, 4, 7, 0, 0, 10, 13, 15, 5, 12, 2, 3, 6, 3, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 6, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (394, 286, 65.70700073242188, -167.83920288085938, 3583, -10105, 8941, -16601, 5, 34303, 0, 0, 200, 581, 516, 295, 202, 55, 28, 1489, 2346, 3018, 2636, 2906, 6020, 12097, 6352, 16932, 7760, 8872, 929, 517, 685, 3003, 2495, 3255, 3202, 2549, 3444, 330, 330, 10008, 11099, 7876, 7303, 7860, 8761, 14994, 16898, 17317, 20986, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 11, 14, 15, 5, 11, 3, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 15, 28, 28, 6, 6, 6, 3, 6, 0, 0, 3, 0, 0, 0, 255, 255, [23, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (394, 287, 65.70447540283203, -167.87124633789062, 3573, -10108, 8940, -16604, 5, 34268, 2, 0, 200, 568, 515, 297, 200, 59, 31, 1497, 2354, 3042, 2651, 2929, 6012, 12065, 6336, 16885, 7681, 8659, 921, 525, 677, 3010, 2503, 3277, 3217, 2548, 3444, 330, 330, 10054, 11082, 7883, 7321, 7873, 8774, 14967, 16911, 17264, 20995, 14, 6, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 11, 13, 15, 5, 9, 3, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 15, 28, 28, 6, 6, 6, 3, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (394, 288, 65.70195007324219, -167.90321350097656, 3564, -10111, 8940, -16607, 5, 34233, 2, 0, 197, 514, 520, 297, 172, 49, 32, 1506, 2370, 3058, 2667, 2937, 5869, 11783, 6161, 16411, 7286, 7798, 866, 517, 646, 3003, 2503, 3247, 3188, 2525, 3389, 339, 339, 9985, 10951, 7791, 7257, 7801, 8692, 14845, 16843, 17250, 20935, 14, 8, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 14, 15, 5, 9, 3, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 15, 28, 28, 6, 6, 6, 3, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (394, 289, 65.69942474365234, -167.9351043701172, 3554, -10114, 8939, -16610, 5, 34198, 2, 0, 197, 513, 527, 301, 166, 51, 31, 1506, 2387, 3090, 2683, 2969, 5909, 11854, 6201, 16514, 7310, 7790, 866, 517, 654, 2980, 2495, 3232, 3180, 2525, 3389, 339, 339, 9962, 10918, 7738, 7239, 7748, 8623, 14792, 16720, 17093, 20954, 14, 8, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 14, 15, 5, 11, 3, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 15, 28, 28, 6, 6, 6, 3, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (394, 290, 65.6968994140625, -167.96693420410156, 3545, -10117, 8939, -16613, 5, 34164, 2, 0, 204, 538, 529, 306, 185, 61, 37, 1514, 2395, 3105, 2730, 3008, 6067, 12183, 6376, 16988, 7563, 8146, 889, 525, 670, 3003, 2503, 3255, 3202, 2502, 3389, 339, 339, 9939, 10934, 7791, 7266, 7761, 8664, 14792, 16760, 17171, 21051, 13, 7, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 13, 15, 5, 9, 3, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 15, 28, 28, 6, 6, 6, 3, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (394, 291, 65.69436645507812, -167.99867248535156, 3535, -10120, 8938, -16616, 5, 34129, 2, 0, 209, 569, 526, 314, 201, 67, 48, 1514, 2395, 3129, 2761, 3055, 6266, 12591, 6582, 17565, 7879, 8635, 921, 540, 693, 3003, 2488, 3255, 3180, 2502, 3375, 338, 338, 9962, 10835, 7745, 7248, 7748, 8643, 14739, 16637, 17145, 20923, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 8, 7, 4, 5, 4, 7, 0, 0, 11, 13, 15, 5, 14, 3, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 15, 28, 28, 6, 6, 6, 3, 6, 0, 0, 2, 0, 0, 0, 255, 255, [81, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (394, 292, 65.69184112548828, -168.0303497314453, 3526, -10123, 8938, -16619, 6, 34095, 2, 0, 220, 651, 526, 318, 234, 85, 48, 1505, 2386, 3121, 2785, 3094, 6590, 13265, 6963, 18615, 8567, 9875, 1015, 564, 740, 3010, 2503, 3255, 3188, 2456, 3361, 345, 345, 9870, 10868, 7783, 7302, 7761, 8650, 14739, 16678, 17144, 20990, 13, 4, 6, 15, 15, 15, 15, 0, 10, 5, 8, 7, 4, 5, 4, 7, 0, 0, 10, 12, 15, 5, 9, 3, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 15, 28, 28, 6, 6, 6, 3, 6, 0, 12383, 49, 43, 250, 248, 71, 131, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (395, 287, 65.71517181396484, -167.87623596191406, 3573, -10124, 8941, -16605, 5, 34268, 0, 0, 198, 542, 513, 300, 183, 60, 29, 1496, 2343, 3027, 2635, 2904, 5886, 11824, 6182, 16478, 7447, 8243, 888, 511, 654, 3031, 2498, 3290, 3230, 2519, 3464, 340, 340, 10093, 11046, 7932, 7323, 7919, 8816, 14994, 16941, 17302, 21015, 13, 7, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 13, 15, 5, 10, 3, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 0, 3, 0, 0, 0, 255, 255, [23, -97, -114, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (395, 288, 65.71263885498047, -167.908203125, 3564, -10127, 8941, -16608, 5, 34233, 2, 0, 194, 500, 516, 295, 158, 47, 25, 1496, 2360, 3035, 2643, 2912, 5775, 11590, 6048, 16115, 7146, 7586, 841, 511, 638, 3001, 2498, 3260, 3186, 2519, 3409, 342, 342, 9957, 10878, 7800, 7279, 7815, 8713, 14916, 16818, 17263, 20857, 13, 8, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 13, 13, 15, 5, 10, 3, 3, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (395, 289, 65.71009826660156, -167.94012451171875, 3554, -10130, 8940, -16611, 6, 34198, 1, 0, 198, 505, 516, 299, 159, 57, 29, 1505, 2368, 3051, 2659, 2936, 5847, 11746, 6127, 16305, 7226, 7673, 849, 511, 646, 2994, 2490, 3229, 3186, 2519, 3422, 349, 349, 9957, 10861, 7762, 7252, 7743, 8645, 14838, 16831, 17237, 20876, 13, 8, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 13, 13, 15, 5, 12, 3, 3, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (395, 290, 65.70755767822266, -167.97195434570312, 3545, -10133, 8940, -16614, 6, 34164, 2, 0, 202, 530, 516, 305, 170, 59, 33, 1487, 2359, 3051, 2690, 2967, 5974, 12003, 6285, 16740, 7471, 8037, 888, 534, 661, 3024, 2498, 3275, 3223, 2474, 3422, 356, 356, 9957, 10928, 7893, 7332, 7847, 8740, 14855, 16776, 17249, 21150, 13, 7, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 12, 15, 5, 10, 3, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 12421, 49, 43, 250, 248, 71, 131, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (395, 291, 65.70501708984375, -168.0037078857422, 3535, -10136, 8939, -16617, 6, 34129, 1, 0, 211, 587, 521, 310, 202, 76, 50, 1495, 2367, 3067, 2738, 3014, 6259, 12580, 6585, 17570, 7971, 8892, 935, 550, 701, 3061, 2505, 3297, 3223, 2541, 3409, 340, 340, 9979, 10894, 7916, 7332, 7873, 8761, 14838, 16775, 17160, 20953, 13, 6, 6, 15, 15, 15, 15, 0, 10, 5, 7, 8, 4, 5, 4, 7, 0, 0, 11, 12, 15, 4, 8, 3, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 3, 6, 0, 0, 2, 0, 0, 0, 255, 255, [-47, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (396, 288, 65.72332000732422, -167.9132080078125, 3564, -10143, 8942, -16608, 5, 34233, 2, 0, 193, 492, 506, 293, 149, 65528, 23, 1499, 2334, 3021, 2614, 2881, 5710, 11442, 5980, 15879, 7044, 7474, 823, 504, 637, 3017, 2504, 3268, 3212, 2535, 3451, 347, 347, 10063, 11038, 7836, 7335, 7844, 8742, 14915, 16850, 17220, 20894, 13, 8, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 13, 14, 15, 5, 12, 2, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 0, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (396, 289, 65.72077178955078, -167.94512939453125, 3554, -10146, 8941, -16611, 6, 34198, 2, 0, 195, 501, 510, 300, 157, 65528, 28, 1481, 2334, 3013, 2621, 2904, 5781, 11557, 6051, 16093, 7147, 7624, 847, 504, 637, 3017, 2504, 3253, 3205, 2490, 3410, 332, 332, 10017, 10938, 7821, 7291, 7805, 8707, 14853, 16850, 17207, 21072, 13, 8, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 13, 14, 15, 5, 12, 2, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 0, 6, 0, 12431, 49, 44, 245, 245, 71, 131, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0]),
        (396, 290, 65.71821594238281, -167.9770050048828, 3545, -10149, 8941, -16614, 9, 34164, 1, 0, 200, 526, 511, 301, 170, 65528, 35, 1480, 2350, 3029, 2645, 2928, 5907, 11842, 6208, 16528, 7384, 7988, 870, 527, 661, 3054, 2504, 3291, 3235, 2490, 3424, 354, 354, 10039, 10988, 7958, 7395, 7902, 8811, 14853, 16836, 17231, 20852, 13, 7, 6, 15, 15, 15, 15, 0, 10, 5, 8, 8, 4, 5, 4, 7, 0, 0, 12, 13, 15, 5, 12, 2, 2, 6, 3, 15, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 6, 6, 6, 0, 6, 0, 0, 2, 0, 0, 0, 255, 255, [83, -97, 14, -111, 0, 0], [13, -128, -114, 4, 0, 0, 11, 3, 20, 1], [0, 0, 0, 0, 0])], 
      dtype=[('mxd03_granule_row', '<i2'), ('mxd03_granule_column', '<i2'), ('mxd03_latitude', '<f4'), ('mxd03_longitude', '<f4'), ('mxd03_sensor_zenith', '<i2'), ('mxd03_sensor_azimuth', '<i2'), ('mxd03_solar_zenith', '<i2'), ('mxd03_solar_azimuth', '<i2'), ('mxd03_height', '<i2'), ('mxd03_range', '<u2'), ('mxd03_land_sea_mask', '|u1'), ('mxd03_gflags', '|u1'), ('mxd02_band_1A', '<u2'), ('mxd02_band_2A', '<u2'), ('mxd02_band_3A', '<u2'), ('mxd02_band_4A', '<u2'), ('mxd02_band_5A', '<u2'), ('mxd02_band_6A', '<u2'), ('mxd02_band_7A', '<u2'), ('mxd02_band_8', '<u2'), ('mxd02_band_9', '<u2'), ('mxd02_band_10', '<u2'), ('mxd02_band_11', '<u2'), ('mxd02_band_12', '<u2'), ('mxd02_band_13lo', '<u2'), ('mxd02_band_13hi', '<u2'), ('mxd02_band_14lo', '<u2'), ('mxd02_band_14hi', '<u2'), ('mxd02_band_15', '<u2'), ('mxd02_band_16', '<u2'), ('mxd02_band_17', '<u2'), ('mxd02_band_18', '<u2'), ('mxd02_band_19', '<u2'), ('mxd02_band_20', '<u2'), ('mxd02_band_21', '<u2'), ('mxd02_band_22', '<u2'), ('mxd02_band_23', '<u2'), ('mxd02_band_24', '<u2'), ('mxd02_band_25', '<u2'), ('mxd02_band_26', '<u2'), ('mxd02_band_26B', '<u2'), ('mxd02_band_27', '<u2'), ('mxd02_band_28', '<u2'), ('mxd02_band_29', '<u2'), ('mxd02_band_30', '<u2'), ('mxd02_band_31', '<u2'), ('mxd02_band_32', '<u2'), ('mxd02_band_33', '<u2'), ('mxd02_band_34', '<u2'), ('mxd02_band_35', '<u2'), ('mxd02_band_36', '<u2'), ('mxd02_band_uncertainity_1A', '|u1'), ('mxd02_band_uncertainity_2A', '|u1'), ('mxd02_band_uncertainity_3A', '|u1'), ('mxd02_band_uncertainity_4A', '|u1'), ('mxd02_band_uncertainity_5A', '|u1'), ('mxd02_band_uncertainity_6A', '|u1'), ('mxd02_band_uncertainity_7A', '|u1'), ('mxd02_band_uncertainity_8', '|u1'), ('mxd02_band_uncertainity_9', '|u1'), ('mxd02_band_uncertainity_10', '|u1'), ('mxd02_band_uncertainity_11', '|u1'), ('mxd02_band_uncertainity_12', '|u1'), ('mxd02_band_uncertainity_13lo', '|u1'), ('mxd02_band_uncertainity_13hi', '|u1'), ('mxd02_band_uncertainity_14lo', '|u1'), ('mxd02_band_uncertainity_14hi', '|u1'), ('mxd02_band_uncertainity_15', '|u1'), ('mxd02_band_uncertainity_16', '|u1'), ('mxd02_band_uncertainity_17', '|u1'), ('mxd02_band_uncertainity_18', '|u1'), ('mxd02_band_uncertainity_19', '|u1'), ('mxd02_band_uncertainity_20', '|u1'), ('mxd02_band_uncertainity_21', '|u1'), ('mxd02_band_uncertainity_22', '|u1'), ('mxd02_band_uncertainity_23', '|u1'), ('mxd02_band_uncertainity_24', '|u1'), ('mxd02_band_uncertainity_25', '|u1'), ('mxd02_band_uncertainity_26', '|u1'), ('mxd02_band_uncertainity_26B', '|u1'), ('mxd02_band_uncertainity_27', '|u1'), ('mxd02_band_uncertainity_28', '|u1'), ('mxd02_band_uncertainity_29', '|u1'), ('mxd02_band_uncertainity_30', '|u1'), ('mxd02_band_uncertainity_31', '|u1'), ('mxd02_band_uncertainity_32', '|u1'), ('mxd02_band_uncertainity_33', '|u1'), ('mxd02_band_uncertainity_34', '|u1'), ('mxd02_band_uncertainity_35', '|u1'), ('mxd02_band_uncertainity_36', '|u1'), ('mxd02_band_nsamples_1A', '|i1'), ('mxd02_band_nsamples_2A', '|i1'), ('mxd02_band_nsamples_3A', '|i1'), ('mxd02_band_nsamples_4A', '|i1'), ('mxd02_band_nsamples_5A', '|i1'), ('mxd02_band_nsamples_6A', '|i1'), ('mxd02_band_nsamples_7A', '|i1'), ('reserved_20120221a', '|u1'), ('mxd11_lst', '<u2'), ('mxd11_qc', '<u2'), ('mxd11_error_lst', '<u2'), ('mxd11_emis31', '<u2'), ('mxd11_emis32', '<u2'), ('mxd11_view_angle', '|u1'), ('mxd11_view_time', '|u1'), ('mxd35_cloud_mask', '|i1', (6,)), ('mxd35_quality_assurance', '|i1', (10,)), ('reserved_20120221b', '|u1', (5,))])

FILE_NAME = tempfile.mktemp(".nc")

class CompoundAlignTestCase(unittest.TestCase):

    def setUp(self):
        self.file = FILE_NAME
        dataset = netCDF4.Dataset(self.file, "w")
        # Create the netCDF variable for the cell records, store the cell
        # records in the variable, and give the variable a md5sum
        # attribute.
        cell_cmp_dtype = dataset.createCompoundType(cells.dtype,"cell_cmp_dtype")
        dataset.createDimension("number_cells", cells.size)
        v_cells = dataset.createVariable("cells",cell_cmp_dtype,"number_cells")
        v_cells[:] = cells
        dataset.close()

    def tearDown(self):
        # Remove the temporary files
        os.remove(self.file)

    def runTest(self):
        f = netCDF4.Dataset(self.file, 'r')
        new_cells = f.variables["cells"][:]
        assert new_cells.shape == cells.shape 
        assert new_cells.dtype.names == cells.dtype.names
        for name in cells.dtype.names:
            assert cells[name].dtype == new_cells[name].dtype
            assert cells[name].shape == new_cells[name].shape
            assert_array_equal(cells[name],new_cells[name])
        f.close()

if __name__ == '__main__':
    unittest.main()


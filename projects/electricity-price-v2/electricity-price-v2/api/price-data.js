/**
 * 电价数据服务 - 从主站提取数据供电费清单处理器使用
 * 部署地址：/electricity/api/price-data.js
 * 更新：2026年3月电价数据
 */

// 31省份电价数据（2026年2月+3月版本）
const PROVINCE_PRICE_DATA = {
  // ===== 山东 =====
  "山东": {
    "2026": {
      "2": {
        "deepValley": { price: 0.2401, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4802, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7064, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0693, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.2246, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "3": {
        "deepValley": { price: 0.1815, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.2777, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6145, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.9506, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.0948, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  
  // ===== 河南 =====
  "河南": {
    "2026": {
      "2": {
        "deepValley": { price: 0.2804, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5608, hours: [11,12,13,14], name: "低谷" },
        "flat": { price: 0.7842, hours: [6,7,8,9,10,15,16,17,22,23], name: "平段" },
        "high": { price: 1.1203, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.2323, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "3": {
        "deepValley": { price: 0.2804, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4069, hours: [11,12,13,14], name: "低谷" },
        "flat": { price: 0.7155, hours: [6,7,8,9,10,15,16,17,22,23], name: "平段" },
        "high": { price: 1.1196, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.2323, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 浙江 =====
  "浙江": {
    "2026": {
      "2": {
        "deepValley": { price: 0.1829, hours: [11,12,13], name: "深谷" },
        "valley": { price: 0.3658, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.7308, hours: [8,9,10,14,15,16,17,22,23], name: "平段" },
        "high": { price: 1.0962, hours: [19,20,21], name: "高峰" },
        "peak": { price: 1.2058, hours: [18], name: "尖峰" },
        "cycles": 2
      },
      "3": {
        "deepValley": { price: 0.1829, hours: [11,12,13], name: "深谷" },
        "valley": { price: 0.3507, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.7793, hours: [8,9,10,14,15,16,17,22,23], name: "平段" },
        "high": { price: 1.2859, hours: [19,20,21], name: "高峰" },
        "peak": { price: 1.4145, hours: [18], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  
  // ===== 广东 =====
  "广东": {
    "2026": {
      "2": {
        "deepValley": { price: 0.2205, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4410, hours: [8,9,10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7203, hours: [16,17,22,23], name: "平段" },
        "high": { price: 1.0805, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1886, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "3": {
        "deepValley": { price: 0.2205, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.2797, hours: [8,9,10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6906, hours: [16,17,22,23], name: "平段" },
        "high": { price: 1.1547, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.4365, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  
  // ===== 江苏 =====
  "江苏": {
    "2026": {
      "2": {
        "deepValley": { price: 0.2408, hours: [11,12,13], name: "深谷" },
        "valley": { price: 0.4816, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.7224, hours: [8,9,10,14,15,16,17,22,23], name: "平段" },
        "high": { price: 1.0836, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1920, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "3": {
        "deepValley": { price: 0.2408, hours: [11,12,13], name: "深谷" },
        "valley": { price: 0.3858, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.6106, hours: [8,9,10,14,15,16,17,22,23], name: "平段" },
        "high": { price: 0.8872, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.9759, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  
  // ===== 河北 =====
  "河北": {
    "2026": {
      "2": {
        "deepValley": { price: 0.2602, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5204, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7806, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0408, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1449, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "3": {
        "deepValley": { price: 0.2602, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3687, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6425, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.9163, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.0492, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 四川 =====
  "四川": {
    "2026": {
      "1": {
        "deepValley": { price: 0.4010, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4010, hours: [], name: "低谷" },
        "flat": { price: 0.8023, hours: [8,12,13,14,21,22,23], name: "平段" },
        "high": { price: 1.2037, hours: [9,10,11,15,16,17,18,19,20], name: "高峰" },
        "peak": { price: 1.2037, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "2": {
        "deepValley": { price: 0.4010, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4010, hours: [], name: "低谷" },
        "flat": { price: 0.8023, hours: [8,12,13,14,21,22,23], name: "平段" },
        "high": { price: 1.2037, hours: [9,10,11,15,16,17,18,19,20], name: "高峰" },
        "peak": { price: 1.2037, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "3": {
        "deepValley": { price: 0.3299, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.3299, hours: [], name: "低谷" },
        "flat": { price: 0.6813, hours: [8,12,13,14,21,22,23], name: "平段" },
        "high": { price: 1.0326, hours: [9,10,11,15,16,17,18,19,20], name: "高峰" },
        "peak": { price: 1.2200, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  
  // ===== 新增省份：上海 =====
  "上海": {
    "2026": {
      "3": {
        "deepValley": { price: 0.1955, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3884, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7099, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0956, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.2052, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  
  // ===== 新增省份：天津 =====
  "天津": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3559, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6934, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0309, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1340, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：湖南 =====
  "湖南": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3102, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6546, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.9996, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.0996, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：重庆 =====
  "重庆": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3438, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7187, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0814, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1895, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：安徽 =====
  "安徽": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.295, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.5915, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.9466, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.0413, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：湖北 =====
  "湖北": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4231, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6273, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.8198, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.9415, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：福建 =====
  "福建": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3342, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.5653, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.7781, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.8559, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：北京 =====
  "北京": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4074, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6406, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.8738, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.9612, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：江西 =====
  "江西": {
    "2026": {
      "3": {
        "deepValley": { price: 0.3596, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4006, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6467, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.8928, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.9821, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：山西 =====
  "山西": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4095, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.5656, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.7358, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.8094, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：陕西 =====
  "陕西": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3715, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6078, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.8441, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.9285, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：贵州 =====
  "贵州": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3495, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.5918, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.8342, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.9176, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：广西 =====
  "广西": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4931, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6619, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.8307, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.9138, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：新疆 =====
  "新疆": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3663, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.5180, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.7099, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.7809, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：海南 =====
  "海南": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4184, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7376, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.1100, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.2210, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：辽宁 =====
  "辽宁": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3994, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.4990, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.5985, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.6584, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：吉林 =====
  "吉林": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4661, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6534, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.8407, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.9248, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：黑龙江 =====
  "黑龙江": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4724, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6257, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.7790, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.8569, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：内蒙古西 =====
  "内蒙古西": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.2900, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.4524, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.6651, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.7316, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：内蒙古东 =====
  "内蒙古东": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3349, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.4362, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.5688, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.6257, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：青海 =====
  "青海": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.2575, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.4422, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.6212, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.6833, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：甘肃 =====
  "甘肃": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.2459, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.4573, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.4979, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.5477, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：宁夏 =====
  "宁夏": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3399, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.4956, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.4663, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.5129, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  
  // ===== 新增省份：云南（暂未公布，使用默认值） =====
  "云南": {
    "2026": {
      "3": {
        "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.35, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.55, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 0.75, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 0.825, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  }
};

// 默认配置（其他省份使用）
const DEFAULT_PRICE_CONFIG = {
  "deepValley": { price: 0.25, hours: [0,1,2,3,4,5], name: "深谷" },
  "valley": { price: 0.50, hours: [10,11,12,13,14,15], name: "低谷" },
  "flat": { price: 0.75, hours: [6,7,8,9,16,17,22,23], name: "平段" },
  "high": { price: 1.10, hours: [18,19,20,21], name: "高峰" },
  "peak": { price: 1.25, hours: [], name: "尖峰" },
  "cycles": 1
};

/**
 * 获取省份电价数据
 * @param {string} province - 省份名称
 * @param {number} year - 年份
 * @param {number} month - 月份
 * @returns {Object} 电价数据
 */
function getProvincePriceData(province, year, month) {
  const yearStr = String(year);
  const monthStr = String(month);
  
  if (PROVINCE_PRICE_DATA[province] && 
      PROVINCE_PRICE_DATA[province][yearStr] && 
      PROVINCE_PRICE_DATA[province][yearStr][monthStr]) {
    return PROVINCE_PRICE_DATA[province][yearStr][monthStr];
  }
  
  // 返回默认配置
  return DEFAULT_PRICE_CONFIG;
}

/**
 * 获取省份列表
 * @returns {Array} 省份名称列表
 */
function getProvincesList() {
  return Object.keys(PROVINCE_PRICE_DATA);
}

/**
 * 获取充放电时段配置
 * @param {Object} priceData - 电价数据
 * @returns {Array} 24小时充放电状态
 */
function getChargeDischargeSchedule(priceData) {
  const schedule = [];
  
  for (let hour = 0; hour < 24; hour++) {
    let period = 'flat';
    let action = 'idle';
    
    // 判断时段
    if (priceData.deepValley && priceData.deepValley.hours.includes(hour)) {
      period = 'deepValley';
      action = 'charge';
    } else if (priceData.valley && priceData.valley.hours.includes(hour)) {
      period = 'valley';
      action = 'charge';
    } else if (priceData.flat && priceData.flat.hours.includes(hour)) {
      period = 'flat';
      action = 'idle';
    } else if (priceData.high && priceData.high.hours.includes(hour)) {
      period = 'high';
      action = 'discharge';
    } else if (priceData.peak && priceData.peak.hours.includes(hour)) {
      period = 'peak';
      action = 'discharge';
    }
    
    schedule.push({
      hour,
      period,
      action,
      price: priceData[period] ? priceData[period].price : 0
    });
  }
  
  return schedule;
}

/**
 * 获取循环次数
 * @param {string} province - 省份名称
 * @param {number} month - 月份
 * @returns {number} 循环次数（1或2）
 */
function getCycleCount(province, month) {
  const priceData = getProvincePriceData(province, 2026, month);
  return priceData.cycles || 1;
}

// 导出（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    getProvincePriceData,
    getProvincesList,
    getChargeDischargeSchedule,
    getCycleCount,
    PROVINCE_PRICE_DATA
  };
}

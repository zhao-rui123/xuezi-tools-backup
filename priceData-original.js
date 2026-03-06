/**
 * 电价数据 - 31省份分时电价数据
 * 数据时间：2026年2月
 * 执行范围：电网代理购电工商业用户
 */

const PRICE_DATA = {
  "山东": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2401, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4802, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7064, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0693, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.2246, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "2": {
        "deepValley": { price: 0.2401, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4802, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7064, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0693, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.2246, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "河南": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2804, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5608, hours: [11,12,13,14], name: "低谷" },
        "flat": { price: 0.7842, hours: [6,7,8,9,10,15,16,17,22,23], name: "平段" },
        "high": { price: 1.1203, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.2323, hours: [16,17], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2804, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5608, hours: [11,12,13,14], name: "低谷" },
        "flat": { price: 0.7842, hours: [6,7,8,9,10,15,16,17,22,23], name: "平段" },
        "high": { price: 1.1203, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.2323, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "7": {
        "deepValley": { price: 0.2804, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5608, hours: [11,12,13,14], name: "低谷" },
        "flat": { price: 0.7842, hours: [6,7,8,9,10,15,16,17,22,23], name: "平段" },
        "high": { price: 1.1203, hours: [16,17,18,19], name: "高峰" },
        "peak": { price: 1.2323, hours: [20,21,22], name: "尖峰" },
        "cycles": 1
      },
      "8": {
        "deepValley": { price: 0.2804, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5608, hours: [11,12,13,14], name: "低谷" },
        "flat": { price: 0.7842, hours: [6,7,8,9,10,15,16,17,22,23], name: "平段" },
        "high": { price: 1.1203, hours: [16,17,18,19], name: "高峰" },
        "peak": { price: 1.2323, hours: [20,21,22], name: "尖峰" },
        "cycles": 1
      },
      "12": {
        "deepValley": { price: 0.2804, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5608, hours: [11,12,13,14], name: "低谷" },
        "flat": { price: 0.7842, hours: [6,7,8,9,10,15,16,17,22,23], name: "平段" },
        "high": { price: 1.1203, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.2323, hours: [16,17], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "浙江": {
    "2026": {
      "1": {
        "deepValley": { price: 0.1829, hours: [11,12,13], name: "深谷" },
        "valley": { price: 0.3658, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.7308, hours: [8,9,10,14,15,16,17,22,23], name: "平段" },
        "high": { price: 1.0962, hours: [19,20,21], name: "高峰" },
        "peak": { price: 1.2058, hours: [18], name: "尖峰" },
        "cycles": 2
      },
      "2": {
        "deepValley": { price: 0.1829, hours: [11,12,13], name: "深谷" },
        "valley": { price: 0.3658, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.7308, hours: [8,9,10,14,15,16,17,22,23], name: "平段" },
        "high": { price: 1.0962, hours: [19,20,21], name: "高峰" },
        "peak": { price: 1.2058, hours: [18], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "广东": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2205, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4410, hours: [8,9,10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7203, hours: [16,17,22,23], name: "平段" },
        "high": { price: 1.0805, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1886, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "2": {
        "deepValley": { price: 0.2205, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4410, hours: [8,9,10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7203, hours: [16,17,22,23], name: "平段" },
        "high": { price: 1.0805, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1886, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "江苏": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2408, hours: [11,12,13], name: "深谷" },
        "valley": { price: 0.4816, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.7224, hours: [8,9,10,14,15,16,17,22,23], name: "平段" },
        "high": { price: 1.0836, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1920, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "2": {
        "deepValley": { price: 0.2408, hours: [11,12,13], name: "深谷" },
        "valley": { price: 0.4816, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.7224, hours: [8,9,10,14,15,16,17,22,23], name: "平段" },
        "high": { price: 1.0836, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1920, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "河北": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2602, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5204, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7806, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0408, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1449, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2602, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5204, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7806, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0408, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1449, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
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
      "7": {
        "deepValley": { price: 0.4010, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4010, hours: [], name: "低谷" },
        "flat": { price: 0.8023, hours: [8,12,13,14,21,22,23], name: "平段" },
        "high": { price: 1.2037, hours: [9,10,11,15,16,17,18,19,20], name: "高峰" },
        "peak": { price: 1.2037, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "8": {
        "deepValley": { price: 0.4010, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4010, hours: [], name: "低谷" },
        "flat": { price: 0.8023, hours: [8,12,13,14,21,22,23], name: "平段" },
        "high": { price: 1.2037, hours: [9,10,11,15,16,17,18,19,20], name: "高峰" },
        "peak": { price: 1.2037, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "北京": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2208, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4416, hours: [23], name: "低谷" },
        "flat": { price: 0.7360, hours: [8,9,10,12,13,14,15,22], name: "平段" },
        "high": { price: 1.1040, hours: [16,17,18,19,20,21], name: "高峰" },
        "peak": { price: 1.1776, hours: [11], name: "尖峰" },
        "cycles": 2
      },
      "2": {
        "deepValley": { price: 0.2208, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4416, hours: [23], name: "低谷" },
        "flat": { price: 0.7360, hours: [8,9,10,12,13,14,15,22], name: "平段" },
        "high": { price: 1.1040, hours: [16,17,18,19,20,21], name: "高峰" },
        "peak": { price: 1.1776, hours: [11], name: "尖峰" },
        "cycles": 2
      },
      "7": {
        "deepValley": { price: 0.2208, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4416, hours: [23], name: "低谷" },
        "flat": { price: 0.7360, hours: [8,9,10,12,13,14,15,22], name: "平段" },
        "high": { price: 1.1040, hours: [10,13,14,15,17,18,19,20,21], name: "高峰" },
        "peak": { price: 1.1776, hours: [11,12,16], name: "尖峰" },
        "cycles": 2
      },
      "8": {
        "deepValley": { price: 0.2208, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4416, hours: [23], name: "低谷" },
        "flat": { price: 0.7360, hours: [8,9,10,12,13,14,15,22], name: "平段" },
        "high": { price: 1.1040, hours: [10,13,14,15,17,18,19,20,21], name: "高峰" },
        "peak": { price: 1.1776, hours: [11,12,16], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "上海": {
    "2026": {
      "1": {
        "deepValley": { price: 0.1986, hours: [0,1,2,3,4,5,6], name: "深谷" },
        "valley": { price: 0.3972, hours: [7,22,23], name: "低谷" },
        "flat": { price: 0.6620, hours: [8,9,10,15,16,17], name: "平段" },
        "high": { price: 0.9930, hours: [11,18,19,20,21], name: "高峰" },
        "peak": { price: 1.0592, hours: [12,13,14], name: "尖峰" },
        "cycles": 2
      },
      "2": {
        "deepValley": { price: 0.1986, hours: [0,1,2,3,4,5,6], name: "深谷" },
        "valley": { price: 0.3972, hours: [7,22,23], name: "低谷" },
        "flat": { price: 0.6620, hours: [8,9,10,15,16,17], name: "平段" },
        "high": { price: 0.9930, hours: [11,18,19,20,21], name: "高峰" },
        "peak": { price: 1.0592, hours: [12,13,14], name: "尖峰" },
        "cycles": 2
      },
      "7": {
        "deepValley": { price: 0.1986, hours: [0,1,2,3,4,5,6], name: "深谷" },
        "valley": { price: 0.3972, hours: [7,22,23], name: "低谷" },
        "flat": { price: 0.6620, hours: [8,9,10,15,16,17], name: "平段" },
        "high": { price: 0.9930, hours: [11,18,19,20,21], name: "高峰" },
        "peak": { price: 1.0592, hours: [12,13,14], name: "尖峰" },
        "cycles": 2
      },
      "8": {
        "deepValley": { price: 0.1986, hours: [0,1,2,3,4,5,6], name: "深谷" },
        "valley": { price: 0.3972, hours: [7,22,23], name: "低谷" },
        "flat": { price: 0.6620, hours: [8,9,10,15,16,17], name: "平段" },
        "high": { price: 0.9930, hours: [11,18,19,20,21], name: "高峰" },
        "peak": { price: 1.0592, hours: [12,13,14], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "山西": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2105, hours: [11,12,13,14], name: "深谷" },
        "valley": { price: 0.4210, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.6315, hours: [8,9,10,15,16,17,22,23], name: "平段" },
        "high": { price: 0.9473, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.0526, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "2": {
        "deepValley": { price: 0.2105, hours: [11,12,13,14], name: "深谷" },
        "valley": { price: 0.4210, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.6315, hours: [8,9,10,15,16,17,22,23], name: "平段" },
        "high": { price: 0.9473, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.0526, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "湖北": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2458, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4916, hours: [12,13,14,15,16], name: "低谷" },
        "flat": { price: 0.7374, hours: [6,7,8,9,10,11,17,18,22,23], name: "平段" },
        "high": { price: 1.1061, hours: [19,20,21], name: "高峰" },
        "peak": { price: 1.2290, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2458, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4916, hours: [12,13,14,15,16], name: "低谷" },
        "flat": { price: 0.7374, hours: [6,7,8,9,10,11,17,18,22,23], name: "平段" },
        "high": { price: 1.1061, hours: [19,20,21], name: "高峰" },
        "peak": { price: 1.2290, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "7": {
        "deepValley": { price: 0.2458, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4916, hours: [12,13,14,15,16], name: "低谷" },
        "flat": { price: 0.7374, hours: [6,7,8,9,10,11,17,18,22,23], name: "平段" },
        "high": { price: 1.1061, hours: [20,21,22], name: "高峰" },
        "peak": { price: 1.2290, hours: [19], name: "尖峰" },
        "cycles": 1
      },
      "8": {
        "deepValley": { price: 0.2458, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4916, hours: [12,13,14,15,16], name: "低谷" },
        "flat": { price: 0.7374, hours: [6,7,8,9,10,11,17,18,22,23], name: "平段" },
        "high": { price: 1.1061, hours: [20,21,22], name: "高峰" },
        "peak": { price: 1.2290, hours: [19], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "湖南": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2385, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4770, hours: [23], name: "低谷" },
        "flat": { price: 0.7155, hours: [6,7,8,9,10,11,12,13,14,15,16,17,22], name: "平段" },
        "high": { price: 1.0733, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1925, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2385, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4770, hours: [23], name: "低谷" },
        "flat": { price: 0.7155, hours: [6,7,8,9,10,11,12,13,14,15,16,17,22], name: "平段" },
        "high": { price: 1.0733, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1925, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "7": {
        "deepValley": { price: 0.2385, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4770, hours: [23], name: "低谷" },
        "flat": { price: 0.7155, hours: [6,7,8,9,10,11,12,13,14,15,16,17,22], name: "平段" },
        "high": { price: 1.0733, hours: [20,21], name: "高峰" },
        "peak": { price: 1.1925, hours: [18,19], name: "尖峰" },
        "cycles": 1
      },
      "8": {
        "deepValley": { price: 0.2385, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4770, hours: [23], name: "低谷" },
        "flat": { price: 0.7155, hours: [6,7,8,9,10,11,12,13,14,15,16,17,22], name: "平段" },
        "high": { price: 1.0733, hours: [20,21], name: "高峰" },
        "peak": { price: 1.1925, hours: [18,19], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "安徽": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2156, hours: [2,3,4,5], name: "深谷" },
        "valley": { price: 0.4312, hours: [0,1,6,7,8,9,10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6468, hours: [16,17,22,23], name: "平段" },
        "high": { price: 0.9702, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.0770, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "2": {
        "deepValley": { price: 0.2156, hours: [2,3,4,5], name: "深谷" },
        "valley": { price: 0.4312, hours: [0,1,6,7,8,9,10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6468, hours: [16,17,22,23], name: "平段" },
        "high": { price: 0.9702, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.0770, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "7": {
        "deepValley": { price: 0.2156, hours: [2,3,4,5], name: "深谷" },
        "valley": { price: 0.4312, hours: [0,1,6,7,8,9,10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6468, hours: [16,17,22,23], name: "平段" },
        "high": { price: 0.9702, hours: [16,17,20,21,22], name: "高峰" },
        "peak": { price: 1.0770, hours: [18,19], name: "尖峰" },
        "cycles": 2
      },
      "8": {
        "deepValley": { price: 0.2156, hours: [2,3,4,5], name: "深谷" },
        "valley": { price: 0.4312, hours: [0,1,6,7,8,9,10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6468, hours: [16,17,22,23], name: "平段" },
        "high": { price: 0.9702, hours: [16,17,20,21,22], name: "高峰" },
        "peak": { price: 1.0770, hours: [18,19], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "福建": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2008, hours: [11,12], name: "深谷" },
        "valley": { price: 0.4016, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.6024, hours: [8,9,10,13,14,15,22,23], name: "平段" },
        "high": { price: 0.9036, hours: [16,17,18,19,20,21], name: "高峰" },
        "peak": { price: 1.0040, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "2": {
        "deepValley": { price: 0.2008, hours: [11,12], name: "深谷" },
        "valley": { price: 0.4016, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.6024, hours: [8,9,10,13,14,15,22,23], name: "平段" },
        "high": { price: 0.9036, hours: [16,17,18,19,20,21], name: "高峰" },
        "peak": { price: 1.0040, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "江西": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2354, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4708, hours: [12,13,14,15,16,17], name: "低谷" },
        "flat": { price: 0.7062, hours: [6,7,8,9,10,11,18,22,23], name: "平段" },
        "high": { price: 1.0593, hours: [19,20,21], name: "高峰" },
        "peak": { price: 1.1770, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2354, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4708, hours: [12,13,14,15,16,17], name: "低谷" },
        "flat": { price: 0.7062, hours: [6,7,8,9,10,11,18,22,23], name: "平段" },
        "high": { price: 1.0593, hours: [19,20,21], name: "高峰" },
        "peak": { price: 1.1770, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "重庆": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2678, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.5356, hours: [], name: "低谷" },
        "flat": { price: 0.8034, hours: [8,12,13,14,21,22,23], name: "平段" },
        "high": { price: 1.2051, hours: [9,10,11,15,16,17,18,19,20], name: "高峰" },
        "peak": { price: 1.2051, hours: [], name: "尖峰" },
        "cycles": 2
      },
      "2": {
        "deepValley": { price: 0.2678, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.5356, hours: [], name: "低谷" },
        "flat": { price: 0.8034, hours: [8,12,13,14,21,22,23], name: "平段" },
        "high": { price: 1.2051, hours: [9,10,11,15,16,17,18,19,20], name: "高峰" },
        "peak": { price: 1.2051, hours: [], name: "尖峰" },
        "cycles": 2
      }
    }
  },
  "天津": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2589, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5178, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7767, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0356, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1392, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2589, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.5178, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.7767, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0356, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1392, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "辽宁": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2725, hours: [11,12,13,14,15], name: "深谷" },
        "valley": { price: 0.5450, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.8175, hours: [8,9,10,16,17,22,23], name: "平段" },
        "high": { price: 1.0900, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1990, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2725, hours: [11,12,13,14,15], name: "深谷" },
        "valley": { price: 0.5450, hours: [0,1,2,3,4,5,6,7], name: "低谷" },
        "flat": { price: 0.8175, hours: [8,9,10,16,17,22,23], name: "平段" },
        "high": { price: 1.0900, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1990, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "吉林": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2856, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.5712, hours: [22,23], name: "低谷" },
        "flat": { price: 0.8568, hours: [8,9,10,11,12,13,14,15,16,17,18,19,20,21], name: "平段" },
        "high": { price: 1.1424, hours: [], name: "高峰" },
        "peak": { price: 1.2566, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2856, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.5712, hours: [22,23], name: "低谷" },
        "flat": { price: 0.8568, hours: [8,9,10,11,12,13,14,15,16,17,18,19,20,21], name: "平段" },
        "high": { price: 1.1424, hours: [], name: "高峰" },
        "peak": { price: 1.2566, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "黑龙江": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2987, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.5974, hours: [22,23], name: "低谷" },
        "flat": { price: 0.8961, hours: [8,9,10,11,12,13,14,15,16,17,18,19,20,21], name: "平段" },
        "high": { price: 1.1948, hours: [], name: "高峰" },
        "peak": { price: 1.3143, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2987, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.5974, hours: [22,23], name: "低谷" },
        "flat": { price: 0.8961, hours: [8,9,10,11,12,13,14,15,16,17,18,19,20,21], name: "平段" },
        "high": { price: 1.1948, hours: [], name: "高峰" },
        "peak": { price: 1.3143, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "陕西": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2356, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4712, hours: [11,12,13,14,15,16], name: "低谷" },
        "flat": { price: 0.7068, hours: [6,7,8,9,10,17,18,22,23], name: "平段" },
        "high": { price: 1.0602, hours: [19,20,21], name: "高峰" },
        "peak": { price: 1.1780, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2356, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4712, hours: [11,12,13,14,15,16], name: "低谷" },
        "flat": { price: 0.7068, hours: [6,7,8,9,10,17,18,22,23], name: "平段" },
        "high": { price: 1.0602, hours: [19,20,21], name: "高峰" },
        "peak": { price: 1.1780, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "甘肃": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2108, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4216, hours: [8,9,10,11,12,13,14,15,16], name: "低谷" },
        "flat": { price: 0.6324, hours: [17,18,19,20,21,22,23], name: "平段" },
        "high": { price: 0.9486, hours: [], name: "高峰" },
        "peak": { price: 1.0435, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2108, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4216, hours: [8,9,10,11,12,13,14,15,16], name: "低谷" },
        "flat": { price: 0.6324, hours: [17,18,19,20,21,22,23], name: "平段" },
        "high": { price: 0.9486, hours: [], name: "高峰" },
        "peak": { price: 1.0435, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "青海": {
    "2026": {
      "1": {
        "deepValley": { price: 0.1856, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.3712, hours: [8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23], name: "低谷" },
        "flat": { price: 0.5568, hours: [], name: "平段" },
        "high": { price: 0.8352, hours: [], name: "高峰" },
        "peak": { price: 0.9187, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.1856, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.3712, hours: [8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23], name: "低谷" },
        "flat": { price: 0.5568, hours: [], name: "平段" },
        "high": { price: 0.8352, hours: [], name: "高峰" },
        "peak": { price: 0.9187, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "宁夏": {
    "2026": {
      "1": {
        "deepValley": { price: 0.1985, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.3970, hours: [8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23], name: "低谷" },
        "flat": { price: 0.5955, hours: [], name: "平段" },
        "high": { price: 0.8933, hours: [], name: "高峰" },
        "peak": { price: 0.9826, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.1985, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.3970, hours: [8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23], name: "低谷" },
        "flat": { price: 0.5955, hours: [], name: "平段" },
        "high": { price: 0.8933, hours: [], name: "高峰" },
        "peak": { price: 0.9826, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "新疆": {
    "2026": {
      "1": {
        "deepValley": { price: 0.1568, hours: [2,3,4,5,6,7,8], name: "深谷" },
        "valley": { price: 0.3136, hours: [0,1,9,10,11,12,13,14,15,16,17], name: "低谷" },
        "flat": { price: 0.4704, hours: [18,19,20,21,22,23], name: "平段" },
        "high": { price: 0.7056, hours: [], name: "高峰" },
        "peak": { price: 0.7762, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.1568, hours: [2,3,4,5,6,7,8], name: "深谷" },
        "valley": { price: 0.3136, hours: [0,1,9,10,11,12,13,14,15,16,17], name: "低谷" },
        "flat": { price: 0.4704, hours: [18,19,20,21,22,23], name: "平段" },
        "high": { price: 0.7056, hours: [], name: "高峰" },
        "peak": { price: 0.7762, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "内蒙古": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2156, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4312, hours: [8,9,10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6468, hours: [16,17,18,19,20,21,22,23], name: "平段" },
        "high": { price: 0.9702, hours: [], name: "高峰" },
        "peak": { price: 1.0672, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2156, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.4312, hours: [8,9,10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6468, hours: [16,17,18,19,20,21,22,23], name: "平段" },
        "high": { price: 0.9702, hours: [], name: "高峰" },
        "peak": { price: 1.0672, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "广西": {
    "2026": {
      "1": {
        "deepValley": { price: 0.1985, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3970, hours: [6,7,8,9,10,11,12,13,14,15,16,17], name: "低谷" },
        "flat": { price: 0.5955, hours: [18,19,20,21,22,23], name: "平段" },
        "high": { price: 0.8933, hours: [], name: "高峰" },
        "peak": { price: 0.9826, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.1985, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.3970, hours: [6,7,8,9,10,11,12,13,14,15,16,17], name: "低谷" },
        "flat": { price: 0.5955, hours: [18,19,20,21,22,23], name: "平段" },
        "high": { price: 0.8933, hours: [], name: "高峰" },
        "peak": { price: 0.9826, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "海南": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2105, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4210, hours: [6,7,8,9,10,11,12,13,14,15,16,17], name: "低谷" },
        "flat": { price: 0.6315, hours: [18,19,20,21,22,23], name: "平段" },
        "high": { price: 0.9473, hours: [], name: "高峰" },
        "peak": { price: 1.0420, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2105, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4210, hours: [6,7,8,9,10,11,12,13,14,15,16,17], name: "低谷" },
        "flat": { price: 0.6315, hours: [18,19,20,21,22,23], name: "平段" },
        "high": { price: 0.9473, hours: [], name: "高峰" },
        "peak": { price: 1.0420, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "贵州": {
    "2026": {
      "1": {
        "deepValley": { price: 0.2256, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4512, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6768, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0152, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1167, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.2256, hours: [0,1,2,3,4,5], name: "深谷" },
        "valley": { price: 0.4512, hours: [10,11,12,13,14,15], name: "低谷" },
        "flat": { price: 0.6768, hours: [6,7,8,9,16,17,22,23], name: "平段" },
        "high": { price: 1.0152, hours: [18,19,20,21], name: "高峰" },
        "peak": { price: 1.1167, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "云南": {
    "2026": {
      "1": {
        "deepValley": { price: 0.1985, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.3970, hours: [8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23], name: "低谷" },
        "flat": { price: 0.5955, hours: [], name: "平段" },
        "high": { price: 0.8933, hours: [], name: "高峰" },
        "peak": { price: 0.9826, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.1985, hours: [0,1,2,3,4,5,6,7], name: "深谷" },
        "valley": { price: 0.3970, hours: [8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23], name: "低谷" },
        "flat": { price: 0.5955, hours: [], name: "平段" },
        "high": { price: 0.8933, hours: [], name: "高峰" },
        "peak": { price: 0.9826, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  },
  "西藏": {
    "2026": {
      "1": {
        "deepValley": { price: 0.1856, hours: [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23], name: "深谷" },
        "valley": { price: 0.3712, hours: [], name: "低谷" },
        "flat": { price: 0.5568, hours: [], name: "平段" },
        "high": { price: 0.8352, hours: [], name: "高峰" },
        "peak": { price: 0.9187, hours: [], name: "尖峰" },
        "cycles": 1
      },
      "2": {
        "deepValley": { price: 0.1856, hours: [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23], name: "深谷" },
        "valley": { price: 0.3712, hours: [], name: "低谷" },
        "flat": { price: 0.5568, hours: [], name: "平段" },
        "high": { price: 0.8352, hours: [], name: "高峰" },
        "peak": { price: 0.9187, hours: [], name: "尖峰" },
        "cycles": 1
      }
    }
  }
};

// 省份备注信息
const PROVINCE_NOTES = {
  "河南": "尖峰：1月、12月17:00-19:00；7-8月20:00-23:00",
  "北京": "夏季（7-8月）尖峰时段为11:00-13:00和16:00-17:00",
  "上海": "夏季（7-8月）尖峰时段为12:00-14:00",
  "湖北": "夏季（7-8月）尖峰时段为19:00",
  "湖南": "夏季（7-8月）尖峰时段为18:00-19:00",
  "安徽": "夏季（7-8月）尖峰时段为18:00-19:00",
  "四川": "丰水期（6-10月）执行特殊电价政策",
  "重庆": "丰水期（6-10月）执行特殊电价政策"
};

// 电价颜色配置
const PRICE_COLORS = {
  "deepValley": "#6366f1",  // 深谷 - 紫色
  "valley": "#3b82f6",      // 低谷 - 蓝色
  "flat": "#22c55e",        // 平段 - 绿色
  "high": "#f97316",        // 高峰 - 橙色
  "peak": "#ef4444"         // 尖峰 - 红色
};

// 电价类型中文名
const PRICE_TYPE_NAMES = {
  "deepValley": "深谷",
  "valley": "低谷",
  "flat": "平段",
  "high": "高峰",
  "peak": "尖峰"
};

// 电价类型排序权重
const PRICE_TYPE_WEIGHTS = {
  "peak": 5,
  "high": 4,
  "flat": 3,
  "valley": 2,
  "deepValley": 1
};

// 导出数据（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    PRICE_DATA,
    PROVINCE_NOTES,
    PRICE_COLORS,
    PRICE_TYPE_NAMES,
    PRICE_TYPE_WEIGHTS
  };
}

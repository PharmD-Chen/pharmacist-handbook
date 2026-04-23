/**
 * 药品数据文件（测试版）
 * 药品数量: 10
 */

const DRUGS_DATA = [
  {
    "id": 1,
    "name": "阿司匹林",
    "dosage_form": "肠溶片",
    "full_name": "(甲)阿司匹林肠溶片",
    "chemical_name": "阿司匹林肠溶片",
    "types": [
      "甲类"
    ],
    "manufacturers": [
      "Bayer S.p.A",
      "上海信谊百路达药业",
      "南京道群医药研发"
    ],
    "specifications": [
      {
        "specification": "100mg/片",
        "manufacturer": "南京道群医药研发",
        "full_manufacturer": "南京道群医药研发有限公司（委托生产企业：南京白敬宇制药有限责任公司）",
        "price": 1.11,
        "unit": "盒",
        "code": "X00847",
        "approval_number": "国药准字H20247035",
        "insurance_code": "XB01ACA056A012030101554"
      },
      {
        "specification": "0.1g/片",
        "manufacturer": "Bayer S.p.A",
        "full_manufacturer": "Bayer S.p.A(Bayer HealthCare Manufacturing S.r.l.)(进口分包:拜耳医药保健有限公司)",
        "price": 13.55,
        "unit": "盒",
        "code": "Y00000013190",
        "approval_number": "国药准字HJ20160685",
        "insurance_code": "XB01ACA056A012020279489"
      },
      {
        "specification": "25mg/片",
        "manufacturer": "上海信谊百路达药业",
        "full_manufacturer": "上海信谊百路达药业有限公司",
        "price": 2.06,
        "unit": "盒",
        "code": "X00461",
        "approval_number": "国药准字H31022475",
        "insurance_code": "XB01ACA056A012010100799"
      }
    ],
    "spec_count": 3,
    "manual": {
      "indications": "",
      "dosage": "",
      "contraindications": "",
      "adverse_reactions": "",
      "interactions": "",
      "pregnancy_category": "",
      "pharmacokinetics": "",
      "precautions": "",
      "atc_code": "",
      "source_file": ""
    }
  },
  {
    "id": 2,
    "name": "复方α-酮酸",
    "dosage_form": "片",
    "full_name": "(乙)复方α-酮酸片[市基]",
    "chemical_name": "复方α-酮酸片",
    "types": [
      "乙类",
      "市基药"
    ],
    "manufacturers": [
      "上海郅见生物医药技术"
    ],
    "specifications": [
      {
        "specification": "0.63g/片",
        "manufacturer": "上海郅见生物医药技术",
        "full_manufacturer": "上海郅见生物医药技术有限公司（委托生产企业：南京白敬宇制药有限责任公司）",
        "price": 31.87,
        "unit": "盒",
        "code": "X00848",
        "approval_number": "国药准字H20243395",
        "insurance_code": "XV02DEF113A001010184440"
      }
    ],
    "spec_count": 1,
    "manual": {
      "indications": "",
      "dosage": "",
      "contraindications": "",
      "adverse_reactions": "",
      "interactions": "",
      "pregnancy_category": "",
      "pharmacokinetics": "",
      "precautions": "",
      "atc_code": "",
      "source_file": ""
    }
  },
  {
    "id": 3,
    "name": "钆特酸葡胺",
    "dosage_form": "注射液",
    "full_name": "(乙10%)钆特酸葡胺注射液",
    "chemical_name": "钆特酸葡胺注射液",
    "types": [],
    "manufacturers": [
      "GUERBET",
      "江苏恒瑞医药"
    ],
    "specifications": [
      {
        "specification": "15ml/瓶",
        "manufacturer": "江苏恒瑞医药",
        "full_manufacturer": "江苏恒瑞医药股份有限公司",
        "price": 26.88,
        "unit": "瓶",
        "code": "X00849",
        "approval_number": "国药准字H20153167",
        "insurance_code": "XV08CAG004B002020101445"
      },
      {
        "specification": "15ml/瓶",
        "manufacturer": "GUERBET",
        "full_manufacturer": "GUERBET（GUERBET）",
        "price": 170.85,
        "unit": "盒",
        "code": "X00257",
        "approval_number": "国药准字HJ20160128",
        "insurance_code": "XV08CAG004B002020178485"
      }
    ],
    "spec_count": 2,
    "manual": {
      "indications": "",
      "dosage": "",
      "contraindications": "",
      "adverse_reactions": "",
      "interactions": "",
      "pregnancy_category": "",
      "pharmacokinetics": "",
      "precautions": "",
      "atc_code": "",
      "source_file": ""
    }
  },
  {
    "id": 4,
    "name": "硫酸羟氯喹",
    "dosage_form": "片",
    "full_name": "(乙)硫酸羟氯喹片[国基]",
    "chemical_name": "硫酸羟氯喹片",
    "types": [
      "乙类",
      "国家基药"
    ],
    "manufacturers": [
      "浙江杭康药业"
    ],
    "specifications": [
      {
        "specification": "0.2g/片",
        "manufacturer": "浙江杭康药业",
        "full_manufacturer": "浙江杭康药业有限公司",
        "price": 4.17,
        "unit": "盒",
        "code": "X00853",
        "approval_number": "国药准字H20249129",
        "insurance_code": "XP01BAQ034A001010104642"
      }
    ],
    "spec_count": 1,
    "manual": {
      "indications": "",
      "dosage": "",
      "contraindications": "",
      "adverse_reactions": "",
      "interactions": "",
      "pregnancy_category": "",
      "pharmacokinetics": "",
      "precautions": "",
      "atc_code": "",
      "source_file": ""
    }
  },
  {
    "id": 5,
    "name": "氯化钾",
    "dosage_form": "注射液",
    "full_name": "(甲)氯化钾注射液[国基]",
    "chemical_name": "氯化钾注射液",
    "types": [
      "甲类",
      "国家基药"
    ],
    "manufacturers": [
      "中国大冢制药",
      "哈尔滨三联药业"
    ],
    "specifications": [
      {
        "specification": "1.5g/支",
        "manufacturer": "哈尔滨三联药业",
        "full_manufacturer": "哈尔滨三联药业股份有限公司",
        "price": 0.16,
        "unit": "支",
        "code": "X00854",
        "approval_number": "国药准字H20084537",
        "insurance_code": "XB05XAL208B002020203662"
      },
      {
        "specification": "1g/支",
        "manufacturer": "中国大冢制药",
        "full_manufacturer": "中国大冢制药有限公司",
        "price": 1.2,
        "unit": "瓶",
        "code": "X00154",
        "approval_number": "国药准字H20053710",
        "insurance_code": "XB05XAL208B002010100967"
      }
    ],
    "spec_count": 2,
    "manual": {
      "indications": "",
      "dosage": "",
      "contraindications": "",
      "adverse_reactions": "",
      "interactions": "",
      "pregnancy_category": "",
      "pharmacokinetics": "",
      "precautions": "",
      "atc_code": "",
      "source_file": ""
    }
  },
  {
    "id": 6,
    "name": "氨茶碱",
    "dosage_form": "注射液",
    "full_name": "(甲)氨茶碱注射液",
    "chemical_name": "氨茶碱注射液",
    "types": [
      "甲类"
    ],
    "manufacturers": [
      "海南紫程众投生物科技",
      "石药银湖制药"
    ],
    "specifications": [
      {
        "specification": "0.25g/支",
        "manufacturer": "海南紫程众投生物科技",
        "full_manufacturer": "海南紫程众投生物科技有限公司（委托生产企业：河北凯威制药有限责任公司）",
        "price": 0.6,
        "unit": "支",
        "code": "X00862",
        "approval_number": "国药准字H20067459",
        "insurance_code": "XR03DAA113B002010102087"
      },
      {
        "specification": "0.25g/支",
        "manufacturer": "石药银湖制药",
        "full_manufacturer": "石药银湖制药有限公司",
        "price": 70.0,
        "unit": "盒",
        "code": "X00069",
        "approval_number": "国药准字H14022613",
        "insurance_code": "XR03DAA113B002020202954"
      }
    ],
    "spec_count": 2,
    "manual": {
      "indications": "",
      "dosage": "",
      "contraindications": "",
      "adverse_reactions": "",
      "interactions": "",
      "pregnancy_category": "",
      "pharmacokinetics": "",
      "precautions": "",
      "atc_code": "",
      "source_file": ""
    }
  },
  {
    "id": 7,
    "name": "氟尿嘧啶",
    "dosage_form": "注射液",
    "full_name": "(甲)氟尿嘧啶注射液[国基]",
    "chemical_name": "氟尿嘧啶注射液",
    "types": [
      "甲类",
      "国家基药"
    ],
    "manufacturers": [
      "津药和平制药"
    ],
    "specifications": [
      {
        "specification": "0.25g/支",
        "manufacturer": "津药和平制药",
        "full_manufacturer": "津药和平（天津）制药有限公司",
        "price": 1.69,
        "unit": "支",
        "code": "X00863",
        "approval_number": "国药准字H12020959",
        "insurance_code": "XL01BCF082B002010200874"
      }
    ],
    "spec_count": 1,
    "manual": {
      "indications": "",
      "dosage": "",
      "contraindications": "",
      "adverse_reactions": "",
      "interactions": "",
      "pregnancy_category": "",
      "pharmacokinetics": "",
      "precautions": "",
      "atc_code": "",
      "source_file": ""
    }
  },
  {
    "id": 8,
    "name": "盐酸贝尼地平",
    "dosage_form": "片",
    "full_name": "(乙10%)盐酸贝尼地平片",
    "chemical_name": "盐酸贝尼地平片",
    "types": [],
    "manufacturers": [
      "Kyowa Kirin Co., Ltd.",
      "山东华素制药"
    ],
    "specifications": [
      {
        "specification": "4mg/片",
        "manufacturer": "山东华素制药",
        "full_manufacturer": "山东华素制药有限公司",
        "price": 27.13,
        "unit": "盒",
        "code": "X00877",
        "approval_number": "国药准字H20184010",
        "insurance_code": "XC08CAB037A001020180517"
      },
      {
        "specification": "8mg/片",
        "manufacturer": "山东华素制药",
        "full_manufacturer": "山东华素制药有限公司",
        "price": 26.9,
        "unit": "盒",
        "code": "X00665",
        "approval_number": "国药准字H20184009",
        "insurance_code": "XC08CAB037A001030180517"
      },
      {
        "specification": "8mg/片",
        "manufacturer": "Kyowa Kirin Co., Ltd.",
        "full_manufacturer": "Kyowa Kirin Co., Ltd.(Kyowa Kirin Co., Ltd. Ube Plant)",
        "price": 56.84,
        "unit": "盒",
        "code": "X00930",
        "approval_number": "国药准字HJ20170111",
        "insurance_code": "XC08CAB037A001020100617"
      }
    ],
    "spec_count": 3,
    "manual": {
      "indications": "",
      "dosage": "",
      "contraindications": "",
      "adverse_reactions": "",
      "interactions": "",
      "pregnancy_category": "",
      "pharmacokinetics": "",
      "precautions": "",
      "atc_code": "",
      "source_file": ""
    }
  },
  {
    "id": 9,
    "name": "美沙拉秦肠溶缓释",
    "dosage_form": "胶囊",
    "full_name": "(甲)美沙拉秦肠溶缓释胶囊",
    "chemical_name": "美沙拉秦肠溶缓释胶囊",
    "types": [
      "甲类"
    ],
    "manufacturers": [
      "海南合瑞制药"
    ],
    "specifications": [
      {
        "specification": "0.375g/粒",
        "manufacturer": "海南合瑞制药",
        "full_manufacturer": "海南合瑞制药股份有限公司",
        "price": 80.48,
        "unit": "盒",
        "code": "X00456",
        "approval_number": "国药准字H20233277",
        "insurance_code": "XA07ECM053E013010305815"
      }
    ],
    "spec_count": 1,
    "manual": {
      "indications": "",
      "dosage": "",
      "contraindications": "",
      "adverse_reactions": "",
      "interactions": "",
      "pregnancy_category": "",
      "pharmacokinetics": "",
      "precautions": "",
      "atc_code": "",
      "source_file": ""
    }
  },
  {
    "id": 10,
    "name": "※▲安奈拉唑钠",
    "dosage_form": "肠溶片",
    "full_name": "※▲(乙10%)安奈拉唑钠肠溶片",
    "chemical_name": "安奈拉唑钠肠溶片",
    "types": [],
    "manufacturers": [
      "轩竹医药科技"
    ],
    "specifications": [
      {
        "specification": "20mg/片",
        "manufacturer": "轩竹医药科技",
        "full_manufacturer": "轩竹(北京)医药科技有限公司(委托生产企业：北京京丰制药集团有限公司)",
        "price": 66.0,
        "unit": "盒",
        "code": "X00299",
        "approval_number": "国药准字H20230014",
        "insurance_code": "XA02BCA393A012010383696"
      }
    ],
    "spec_count": 1,
    "manual": {
      "indications": "",
      "dosage": "",
      "contraindications": "",
      "adverse_reactions": "",
      "interactions": "",
      "pregnancy_category": "",
      "pharmacokinetics": "",
      "precautions": "",
      "atc_code": "",
      "source_file": ""
    }
  }
];

// 导出数据（兼容不同模块系统）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DRUGS_DATA };
}

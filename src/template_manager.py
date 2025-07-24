
import json
import os
from pathlib import Path
from typing import Dict, List

class TemplateManager:
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
    
    def save_template(self, template_name: str, config: Dict) -> bool:
        """保存处理配置到模板文件"""
        try:
            template_path = self.template_dir / f"{template_name}.json"
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"保存模板失败: {str(e)}")
            return False
    
    def load_template(self, template_name: str) -> Dict:
        """从模板文件加载配置"""
        try:
            template_path = self.template_dir / f"{template_name}.json"
            if not template_path.exists():
                return {}
            
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载模板失败: {str(e)}")
            return {}
    
    def delete_template(self, template_name: str) -> bool:
        """删除指定模板"""
        try:
            template_path = self.template_dir / f"{template_name}.json"
            if template_path.exists():
                template_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"删除模板失败: {str(e)}")
            return False
    
    def list_templates(self) -> List[str]:
        """获取所有可用模板列表"""
        templates = []
        for file in self.template_dir.glob("*.json"):
            templates.append(file.stem)
        return sorted(templates)
    
    def get_template_config(self, template_name: str) -> Dict:
        """获取模板配置详情"""
        config = self.load_template(template_name)
        return {
            "template_name": template_name,
            "config": config,
            "file_path": str(self.template_dir / f"{template_name}.json")
        }
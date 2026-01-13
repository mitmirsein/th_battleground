
import subprocess
import os
import sys
from typing import List, Optional, Dict

class EpubBuilder:
    """
    Pandoc을 사용하여 EPUB을 생성하는 핵심 빌더
    Ported from PandocService.ts
    """
    
    def __init__(self, pandoc_path: str = 'pandoc'):
        self.pandoc_path = pandoc_path
        
    def check_availability(self) -> bool:
        """Pandoc 설치 여부 확인"""
        try:
            subprocess.run([self.pandoc_path, '--version'], 
                          capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def build(self, 
              input_path: str, 
              output_path: str, 
              title: str,
              author: Optional[str] = None,
              css_path: Optional[str] = None,
              cover_image: Optional[str] = None,
              fonts: List[str] = [],
              toc_depth: int = 2) -> bool:
        """
        EPUB 생성 실행
        """
        
        # 기본 인자 구성
        cmd = [
            self.pandoc_path,
            input_path,
            '-f', 'markdown',
            '-o', output_path,
            '--standalone',
            '--toc',
            f'--toc-depth={toc_depth}',
            f'--metadata=title:{title}'
        ]
        
        # 저자
        if author:
            cmd.append(f'--metadata=author:{author}')
            
        # 표지 이미지
        if cover_image and os.path.exists(cover_image):
            cmd.append(f'--epub-cover-image={cover_image}')
            
        # CSS 스타일시트
        if css_path and os.path.exists(css_path):
            cmd.append(f'--css={css_path}')
            
        # 폰트 임베딩
        for font in fonts:
            if os.path.exists(font):
                cmd.append(f'--epub-embed-font={font}')
            else:
                print(f"Warning: Font not found: {font}")
                
        # 실행
        try:
            print(f"building EPUB: {output_path}...")
            # print("Command:", " ".join(cmd)) # 디버깅용
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error building EPUB:\n{result.stderr}")
                return False
                
            print("Successfully finished.")
            return True
            
        except Exception as e:
            print(f"Exception during build: {e}")
            return False

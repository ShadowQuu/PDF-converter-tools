from pypdf import PdfReader, PdfWriter
import os

class PdfSecurity:
    @staticmethod
    def encrypt(input_path, output_path, user_password, owner_password=None, progress_callback=None):
        """
        Encrypt PDF with password.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        reader = PdfReader(input_path)
        writer = PdfWriter()

        total_pages = len(reader.pages)
        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            if progress_callback:
                progress_callback(int((i + 1) / total_pages * 100))

        writer.encrypt(user_password, owner_pwd=owner_password)

        with open(output_path, "wb") as f:
            writer.write(f)
            
        return True

    @staticmethod
    def decrypt(input_path, output_path, password, progress_callback=None):
        """
        Decrypt PDF (remove password).
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        reader = PdfReader(input_path)
        
        if reader.is_encrypted:
            # 检查密码是否正确
            if reader.decrypt(password) == 0:  # 解密失败
                if not password:
                    raise ValueError("该文件受密码保护，请输入密码。")
                else:
                    raise ValueError("密码错误，无法解密PDF。")
        # 如果PDF未加密，直接处理

        writer = PdfWriter()
        total_pages = len(reader.pages)
        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            if progress_callback:
                progress_callback(int((i + 1) / total_pages * 100))

        with open(output_path, "wb") as f:
            writer.write(f)
            
        return True
    
    @staticmethod
    def remove_permissions(input_path, output_path, progress_callback=None):
        """
        尝试移除PDF的权限限制（如打印、复制限制），无需密码。
        这适用于那些可以打开但有权限限制的PDF文件。
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        reader = PdfReader(input_path)
        
        # 即使PDF被加密，我们也可以尝试移除权限限制
        # 但需要先用空密码或正确的权限密码尝试解密
        try:
            # 尝试用空密码解密（有时权限密码为空）
            if reader.is_encrypted:
                reader.decrypt("")
        except Exception:
            # 如果无法解密，说明需要用户密码，此方法不适用
            raise ValueError("此PDF需要用户密码才能处理。如果PDF需要密码才能打开，必须提供正确密码。")

        writer = PdfWriter()
        total_pages = len(reader.pages)
        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            if progress_callback:
                progress_callback(int((i + 1) / total_pages * 100))

        # 写入新文件，不设置任何密码或权限限制
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return True

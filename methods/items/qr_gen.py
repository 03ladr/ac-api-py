# https://pypi.org/project/treepoem/
from treepoem import generate_barcode

def generate_code(code_type: str, data: str):
    code = generate_barcode(barcode_type=code_type, data=data)

    # Returning a monochrome instance of the code for filesize reduction via
    # .convert("1")
    return code.convert("1")

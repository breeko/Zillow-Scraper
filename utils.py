def get_zip_from_zillow_url(url):
    try:
        zipcode = url.split("/")[4].split("-")[-1]
    except IndexError:
        zipcode = ""
    return zipcode

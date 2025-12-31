from datetime import date
def get_sun_sign(d: date) -> str:
    md = (d.month, d.day)

    if (md >= (3, 21)) and (md <= (4, 19)):
        return "Aries"
    if (md >= (4, 20)) and (md <= (5, 20)):
        return "Taurus"
    if (md >= (5, 21)) and (md <= (6, 20)):
        return "Gemini"
    if (md >= (6, 21)) and (md <= (7, 22)):
        return "Cancer"
    if (md >= (7, 23)) and (md <= (8, 22)):
        return "Leo"
    if (md >= (8, 23)) and (md <= (9, 22)):
        return "Virgo"
    if (md >= (9, 23)) and (md <= (10, 22)):
        return "Libra"
    if (md >= (10, 23)) and (md <= (11, 21)):
        return "Scorpio"
    if (md >= (11, 22)) and (md <= (12, 21)):
        return "Sagittarius"
    if (md >= (12, 22)) and (md <= (1, 19)):
        return "Capricorn"
    if (md >= (1, 20)) and (md <= (2, 18)):
        return "Aquarius"

    return "Pisces"




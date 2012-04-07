# TODO: Load these from a file:

FSQR_CLIENT_ID = "BLPUAJ020WOMEE1H2HCGOSNYHQBUJBKYDRT250GF4HPAWAJR"
FSQR_CLIENT_SECRET = "OE4SYCASQNYOPAXYTGB300CIDKYUUS1P5Z5MPEGF5OJ1B41U"
FSQR_PUSH_SECRET = "PKGVZKM2ZF2KP4UG2JIJCDUSGKNILQMOMXPEIL0ALG0H1QEW"

if Rails.env.production?
  FSQR_REDIRECT_URI = "https://remindersonthego.com/home/signin"
else
  FSQR_REDIRECT_URI = "http://jrl-lt-lin:8081/home/signin"
end

FSQR_SIGN_IN_URI = "https://foursquare.com/oauth2/authenticate?client_id=#{FSQR_CLIENT_ID}&response_type=code&redirect_uri=#{FSQR_REDIRECT_URI}"

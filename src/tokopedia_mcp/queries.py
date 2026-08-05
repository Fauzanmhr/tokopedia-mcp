"""GraphQL queries for Tokopedia's internal iOS app API.

These are the exact queries the Tokopedia iOS app sends. The responses
are parsed by ``extractors`` into typed models.
"""

GQL_ENDPOINT = "https://gql.tokopedia.com"

SEARCH_PATH = "/graphql/SearchResult/getProductResult"
PRODUCT_PATH = "/graphql/ProductDetails/getPDPLayout"
REVIEWS_PATH = "/graphql/ProductReview/getProductReviewReadingList"

SEARCH_QUERY = """query Search_SearchProduct($params: String!, $query: String!) {
 global_search_navigation(keyword: $query, size: 5, device: "ios", params: $params){
 data {
 source
 keyword
 title
 nav_template
 background
 see_all_applink
 show_topads
 info
 list {
 category_name
 name
 info
 image_url
 subtitle
 strikethrough
 background_url
 logo_url
 applink
 component_id
 }
 component_id
 tracking_option
 }
 }
 searchInspirationCarouselV2(params: $params){
 process_time
 data {
 title
 type
 position
 layout
 tracking_option
 color
 options {
 title
 subtitle
 icon_subtitle
 applink
 banner_image_url
 banner_applink_url
 identifier
 meta
 component_id
 card_button {
  title
  applink
 }
 bundle {
  shop {
  name
  url
  }
  count_sold
  price
  original_price
  discount
  discount_percentage
 }
  product {
 id
 ttsProductID
 name
 price
 price_str
 image_url
 rating
 count_review
 applink
 description
 original_price
 discount
 discount_percentage
 rating_average
 badges {
 title
 image_url
 show
 }
 shop {
 id
 name
 city
 ttsSellerID
 }
 label_groups {
 position
 title
 type
 url
 styles {
 key
 value
 }
 }
 freeOngkir {
 isActive
 image_url
 }
 ads {
 id
 productClickUrl
 productWishlistUrl
 productViewUrl
 }
 wishlist
 component_id
 customvideo_url
 label
 bundle_id
 parent_id
 min_order
 category_id
 stockbar {
 percentage_value
 value
 color
 ttsSkuID
 }
 warehouse_id_default
 sold
 }
 }
 }
 }
 searchInspirationWidget(params: $params){
 data {
 title
 header_title
 header_subtitle
 type
 position
 layout
 options {
 text
 img
 color
 applink
 multi_filters{
  key
  name
  value
  val_min
  val_max
 }
 component_id
 }
 tracking_option
 input_type
 }
 }
 productAds: displayAdsV3(displayParams: $params) {
 status {
 error_code
 message
 }
 header {
 process_time
 total_data
 }
 data{
 id
 ad_ref_key
 redirect
 sticker_id
 sticker_image
 product_click_url
 product_wishlist_url
 shop_click_url
 tag
 creative_id
 log_extra
 product{
 id
 tts_product_id
 tts_sku_id
 parent_id
 name
 wishlist
 image{
  m_url
  s_url
  xs_url
  m_ecs
  s_ecs
  xs_ecs
 }
 uri
 relative_uri
 price_format
 price_range
 campaign {
  discount_percentage
  original_price
 }
 wholesale_price {
  price_format
  quantity_max_format
  quantity_min_format
 }
 count_talk_format
 count_review_format
 category {
  id
 }
 category_breadcrumb
 product_preorder
 product_wholesale
 product_item_sold_payment_verified
 free_return
 product_cashback
 product_new_label
 product_cashback_rate
 product_rating
 product_rating_format
 labels {
  color
  title
 }
 free_ongkir {
  is_active
  img_url
 }
 label_group {
  position
  type
  title
  url
  style {
  key
  value
  }
 }
 top_label
 bottom_label
 product_minimum_order
 customvideo_url
 }
 shop{
 id
 tts_seller_id
 name
 domain
 location
 city
 gold_shop
 gold_shop_badge
 lucky_shop
 uri
 shop_rating_avg
 owner_id
 is_owner
 badges{
  title
  image_url
  show
 }
 }
 applinks
 }
 template {
 is_ad
 }
 }
 searchProductV5(params: $params) {
 header {
 totalData
 responseCode
 keywordProcess
 keywordIntention
 componentID
 meta {
 productListType
 hasPostProcessing
 hasButtonATC
 dynamicFields
 }
 isQuerySafe
 additionalParams
 autocompleteApplink
 backendFilters
 backendFiltersToggle
 }
 data {
 totalDataText
 banner {
 position
 text
 applink
 imageURL
 componentID
 trackingOption
 }
 redirection {
 applink
 }
 related {
 relatedKeyword
 position
 trackingOption
 otherRelated {
  keyword
  applink
  componentID
  products {
  id
  name
  applink
  mediaURL {
  image
  }
  shop {
  name
  city
  }
  badge {
  title
  url
  }
  price {
  text
  number
  }
  freeShipping {
  url
  }
  labelGroups {
  id
  position
  title
  type
  url
  styles {
  key
  value
  }
  }
  rating
  wishlist
  ads {
  id
  productClickURL
  productViewURL
  productWishlistURL
  }
  meta {
  parentID
  warehouseID
  componentID
  isImageBlurred
  }
  }
 }
 }
 suggestion {
 currentKeyword
 suggestion
 query
 text
 componentID
 trackingOption
 }
 ticker {
 id
 text
 query
 applink
 componentID
 trackingOption
 }
 violation {
 headerText
 descriptionText
 imageURL
 ctaApplink
 buttonText
 buttonType
 }
 products {
 id
 ttsProductID
 name
 url
 applink
 mediaURL {
  image
  image300
  image500
  image700
  videoCustom
 }
 shop {
  id
  name
  url
  city
  ttsSellerID
 }
 badge {
  title
  url
 }
 price {
  text
  number
  range
  original
  discountPercentage
 }
 freeShipping {
  url
 }
 labelGroups {
  id
  position
  title
  type
  url
  styles {
  key
  value
  }
 }
 labelGroupsVariant {
  title
  type
  typeVariant
  hexColor
 }
 category {
  id
  name
  breadcrumb
  gaKey
 }
 rating
 wishlist
 ads {
  id
  productClickURL
  productViewURL
  productWishlistURL
  tag
  creativeID
  logExtra
 }
 meta {
  parentID
  warehouseID
  isPortrait
  isImageBlurred
  dynamicFields
 }
 stock {
  sold
  ttsSKUID
 }
 }
 shopWidget {
 headline {
  badge {
  url
  }
  shop {
  id
  imageShop {
  sURL
  }
  City
  name
  ratingScore
  ttsSellerID
  products {
  id
  ttsProductID
  name
  applink
  mediaURL {
  image300
  }
  price {
  text
  original
  discountPercentage
  }
  freeShipping {
  url
  }
  labelGroups {
  position
  title
  type
  styles {
   key
   value
  }
  url
  }
  rating
  meta {
  parentID
  dynamicFields
  }
  shop {
  ttsSellerID
  }
  stock {
  ttsSKUID
  }
  }
  }
 }
 meta {
  applinks
 }
 }
 filters {
 title
 template_name: templateName
 isNew
 subTitle: subtitle
 search: searchInfo {
  searchable
  placeholder
 }
 options {
  name
  key
  value
  icon
  isPopular
  isNew
  hexColor
  inputType
  valMin
  valMax
  Description: description
  child {
  name
  key
  value
  isPopular
  child {
  name
  key
  value
  }
  }
 }
 }
 quickFilters {
 title
 chip_name: chipName
 options {
  name
  key
  value
  icon
  is_popular: isPopular
  is_new: isNew
  hex_color: hexColor
  input_type: inputType
  image_url_active: imageURLActive
  image_url_inactive: imageURLInactive
 }
 }
 sorts {
 name
 key
 value
 }
 }
 }
 fetchLastFilter(param: $params) {
 data {
 title
 description
 category_id_l2
 applink
 tracking_option
 filters {
 title
 key
 name
 value
 }
 component_id
 }
 }
 }"""

PRODUCT_QUERY = """query PDP_getPDPLayout($productId: String, $shopDomain: String, $productKey: String, $apiVersion: Float, $whID: String, $layoutID: String, $userLocation: pdpUserLocation, $extParam: String, $tokonow: pdpTokoNow) {
pdpGetLayout(productID: $productId, shopDomain: $shopDomain, productKey: $productKey, apiVersion: $apiVersion, whID: $whID, layoutID: $layoutID, userLocation: $userLocation, extParam: $extParam, tokonow: $tokonow) {
requestID
name
pdpSession
basicInfo {
productID
initialVariantOptionID
category {
id
name
title
breadcrumbURL
isAdult
isKyc
detail {
id
name
breadcrumbURL
}
ttsID
ttsDetail {
id
name
breadcrumbURL
}
}
menu {
id
name
url
}
shopID
shopName
alias
minOrder
maxOrder
url
catalogID
needPrescription
weight
weightUnit
status
txStats {
transactionReject
transactionSuccess
countSold
itemSoldFmt
}
stats {
rating
countTalk
countView
countReview
}
defaultOngkirEstimation
isTokoNow
totalStockFmt
isGiftable
defaultMediaURL
shopMultilocation {
cityName
}
isBlacklisted
blacklistMessage {
title
description
button
}
weightWording
ttsPID
ttsSKUID
ttsShopID
}
additionalData {
fomoSocialProofs {
name
text
icons
typeIcon
backgroundColor
position
}
}
components {
name
type
kind
data {
... on pdpDataComponentSocialProofV2 {
socialProofContent {
socialProofType
socialProofID
title
subtitle
icon
applink {
appLink
}
bgColor
chevronColor
showChevron
hasSeparator
}
}
... on pdpDataProductMedia {
media {
type
URLOriginal
URLThumbnail
description
videoURLIOS
isAutoplay
index
variantOptionID
URLMaxRes
}
recommendation{
lightIcon
darkIcon
iconText
bottomsheetTitle
recommendation
}
videos {
source
url
}
containerType
liveIndicator {
isLive
channelID
mediaURL
applink
}
showJumpToVideo
}
... on pdpDataProductContent {
name
price {
value
currency
lastUpdateUnix
priceFmt
slashPriceFmt
discPercentage
currencyFmt
valueFmt
}
campaign {
campaignID
campaignType
campaignTypeName
percentageAmount
originalPrice
discountedPrice
originalStock
stock
stockSoldPercentage
endDateUnix
isActive
hideGimmick
isUsingOvo
campaignIdentifier
background
paymentInfoWording
productID
campaignLogo
showStockBar
}
thematicCampaign {
productID
campaignName
background
icon
campaignLogo
superGraphicURL
}
stock {
useStock
value
stockWording
}
variant {
isVariant
}
wholesale {
minQty
price {
value
currency
lastUpdateUnix
}
}
isFreeOngkir {
isActive
imageURL
}
preorder {
duration
timeUnit
isActive
preorderInDays
}
isCashback {
percentage
}
isTradeIn
isOS
isPowerMerchant
isWishlist
isCOD
parentName
isShowPrice
labelIcons {
iconURL
label
}
}
... on pdpDataProductInfo {
row
content {
title
subtitle
applink
}
}
... on pdpDataInfo {
title
applink
isApplink
icon
lightIcon
darkIcon
content {
icon
text
}
separator
}
... on pdpDataProductVariant {
parentID
defaultChild
sizeChart
maxFinalPrice
componentType
landingSubText
socialProof {
bgColor
contents {
name
content
iconURL
}
}
variants {
productVariantID
variantID
name
identifier
option {
productVariantOptionID
variantUnitValueID
value
hex
picture {
url
url100
}
}
}
children {
productID
price
priceFmt
slashPriceFmt
discPercentage
sku
optionID
productName
productURL
picture {
url
url100
}
stock {
stock
isBuyable
stockWording
stockWordingHTML
minimumOrder
maximumOrder
stockFmt
stockCopy
}
isCOD
isWishlist
campaignInfo {
campaignID
campaignType
campaignTypeName
discountPercentage
originalPrice
discountPrice
stock
stockSoldPercentage
endDateUnix
appLinks
isActive
hideGimmick
isUsingOvo
minOrder
campaignIdentifier
background
paymentInfoWording
campaignLogo
showStockBar
}
thematicCampaign {
campaignName
icon
background
productID
campaignLogo
superGraphicURL
}
subText
promo {
value
iconURL
productID
promoPriceFmt
subtitle
applink
color
background
promoType
superGraphicURL
priceAdditionalFmt
separatorColor
bottomsheetParam
promoCodes {
promoID
promoCode
promoCodeType
}
}
currencyFmt
valuePriceFmt
componentPriceType
isTopSold
labelIcons {
iconURL
label
}
ttsPID
ttsSKUID
}
}
... on pdpDataCustomInfo {
icon
title
isApplink
applink
separator
description
label {
value
color
}
lightIcon
darkIcon
}
... on pdpDataComponentReviewV2 {
mostHelpfulReviewParam {
limit
}
}
... on pdpDataProductDetail {
title
content {
type
key
extParam
action
title
subtitle
applink
showAtFront
showAtBottomsheet
infoLink
icon
}
catalogBottomsheet {
actionTitle
bottomSheetTitle
param
}
bottomsheet {
actionTitle
bottomSheetTitle
param
}
}
... on pdpDataOneLiner {
productID
oneLinerContent
linkText
applink
separator
isVisible
color
icon
eduLink {
appLink
}
}
... on pdpDataCategoryCarousel {
linkText
titleCarousel
applink
list {
categoryID
icon
title
isApplink
applink
}
}
... on pdpDataBundleComponentInfo {
title
widgetType
productID
whID
}
... on pdpDataDynamicOneLiner {
name
applink
separator
icon
status
chevronPos
text
bgColor
chevronColor
padding {
t
b
}
imageSize {
w
h
}
}
... on pdpDataComponentDynamicOneLinerVariant {
name
applink
separator
icon
status
chevronPos
text
bgColor
chevronColor
padding {
t
b
}
imageSize {
w
h
}
}
... on pdpDataCustomInfoTitle {
title
status
componentName
}
... on pdpDataProductDetailMediaComponent {
title
description
contentMedia {
url
ratio
type
}
show
ctaText
}
... on pdpDataOnGoingCampaign {
campaign {
campaignID
campaignType
campaignTypeName
percentageAmount
originalPrice
discountedPrice
originalStock
stock
stockSoldPercentage
endDateUnix
isActive
hideGimmick
isUsingOvo
campaignIdentifier
background
paymentInfoWording
productID
campaignLogo
showStockBar
}
thematicCampaign {
productID
campaignName
background
icon
campaignLogo
superGraphicURL
}
}
... on pdpDataProductListComponent {
thematicID
queryParam
}
... on pdpDataComponentPromoPrice {
price {
value
currency
lastUpdateUnix
priceFmt
slashPriceFmt
discPercentage
currencyFmt
valueFmt
}
promo {
value
iconURL
productID
promoPriceFmt
subtitle
applink
color
background
promoType
superGraphicURL
priceAdditionalFmt
separatorColor
bottomsheetParam
promoCodes {
promoID
promoCode
promoCodeType
}
}
componentPriceType
}
... on pdpDataComponentSDUIDivKit {
template
}
... on pdpDataComponentShipmentV4 {
data {
productID
warehouse_info {
warehouse_id
is_fulfillment
district_id
postal_code
geolocation
city_name
ttsWarehouseID
}
useBOVoucher
isCOD
metadata
}
}
... on pdpDataComponentShipmentV5 {
data {
productID
warehouse_info {
warehouse_id
is_fulfillment
district_id
postal_code
geolocation
city_name
ttsWarehouseID
}
useBOVoucher
isCOD
metadata
}
}
...on pdpDataAffordabilityGroupLabel {
affordabilityData{
productID
productVouchers {
identifier
type
text
backgroundColor
}
showChevron
chevronColor
appliedVoucherTypeIDs
}
}
}
}
}
}"""

REVIEWS_QUERY = """query productrevGetProductReviewList($productID: String!, $page: Int!, $limit: Int!, $sortBy: String,
$filterBy: String, $opt: String) {
productrevGetProductReviewList(productID: $productID, page: $page, limit: $limit, sortBy: $sortBy,
filterBy: $filterBy, opt: $opt) {
list {
feedbackID
variantName
message
productRating
reviewCreateTime
reviewCreateTimestamp
isAnonymous
isReportable
reviewResponse {
message
createTime
}
user {
userID
fullName
image
url
label
}
imageAttachments {
attachmentID
imageThumbnailUrl
imageUrl
}
videoAttachments {
attachmentID
videoUrl
}
likeDislike {
totalLike
likeStatus
}
stats {
key
formatted
count
}
badRatingReasonFmt
}
shop {
shopID
name
url
image
}
variantFilter {
isUnavailable
ticker
}
hasNext
}
}"""

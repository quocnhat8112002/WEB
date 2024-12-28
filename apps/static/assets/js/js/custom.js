// to get current year
function getYear() {
  var currentDate = new Date();
  var currentYear = currentDate.getFullYear();
  document.querySelector("#displayYear").innerHTML = currentYear;
}

getYear();

// isotope js
$(window).on("load", function () {
  $(".filters_menu li").click(function () {
    $(".filters_menu li").removeClass("active");
    $(this).addClass("active");

    var data = $(this).attr("data-filter");
    $grid.isotope({
      filter: data,
    });
  });

  var $grid = $(".grid").isotope({
    itemSelector: ".all",
    percentPosition: false,
    masonry: {
      columnWidth: ".all",
    },
  });
});

// nice select
$(document).ready(function () {
  $("select").niceSelect();
});

/** google_map js **/
function myMap() {
  var mapProp = {
    center: new google.maps.LatLng(40.712775, -74.005973),
    zoom: 18,
  };
  var map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
}

// client section owl carousel
$(".client_owl-carousel").owlCarousel({
  loop: true,
  margin: 0,
  dots: false,
  nav: true,
  navText: [],
  autoplay: true,
  autoplayHoverPause: true,
  navText: [
    '<i class="fa fa-angle-left" aria-hidden="true"></i>',
    '<i class="fa fa-angle-right" aria-hidden="true"></i>',
  ],
  responsive: {
    0: {
      items: 1,
    },
    768: {
      items: 2,
    },
    1000: {
      items: 2,
    },
  },
});

document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".nav-button"); // Lấy tất cả các nút
  const dynamicImage = document.getElementById("dynamicImage"); // Ảnh thay thế
  const backgroundImage = document.getElementById("backgroundImage"); // Ảnh nền

  buttons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault(); // Ngừng hành động mặc định của thẻ <a>

      // Lấy URL ảnh từ thuộc tính data-image của nút
      const imageUrl = button.getAttribute("data-image");

      // Thay đổi ảnh thay thế
      dynamicImage.src = imageUrl;

      // Thêm hiệu ứng opacity để ảnh thay thế dần xuất hiện
      dynamicImage.style.opacity = 1;

      // Đảm bảo ảnh nền luôn giữ nguyên và không thay đổi
      backgroundImage.style.opacity = 1;

      // Ẩn ảnh cũ (nếu có)
      setTimeout(function () {
        dynamicImage.style.opacity = 1; // Hiển thị ảnh thay đổi
      }, 300); // Chờ 0.3s trước khi thay đổi ảnh
    });
  });
});

# Youtube Data Analysis
![전체](https://user-images.githubusercontent.com/92344242/151417140-5b87eac7-f381-487c-a707-bdcaf53dd9ba.jpeg)

## 주제
- Youtube 데이터 분석하기

## 기획 의도 및 목표
- Raw data를 가공하여 DB로 옮기고 이를 관리해보기
- 예제를 통한 Data Mining 실습해보기

## 개발 기간
2019.11-2019.12

## 데이터베이스 구성

### 원본 데이터 (예시)

|video_id   |trending_date|title             |channel_title|category_id|publish_time    |tags                         |views |likes|dislikes|comment_count|thumbnail_link                                |comments_disabled|ratings_disabled|video_error_or_removed|description                                                                                                                                             |
|-----------|-------------|------------------|-------------|-----------|----------------|-----------------------------|------|-----|--------|-------------|----------------------------------------------|-----------------|----------------|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
|RxGQe4EeEpA|17.14.11     |좋아 by 민서_윤종신_좋니 답가|라푸마코리아       |22         |2017-11-13 16:07|라푸마&#124;"윤종신"&#124;"좋니"&#124;"좋아"&#124;"샬레"&#124;"민서"|156130|1422 |40      |272          |https://i.ytimg.com/vi/RxGQe4EeEpA/default.jpg|FALSE            |FALSE           |FALSE                 |윤종신 '좋니'의 답가 '좋아' 최초 공개!\n그 여자의 이야기를 지금 만나보세요. \n\n좋아, 딱 잊기 좋은 추억 정도야\n난 딱 알맞게 너를 사랑했어.\n\n'좋니'의 그에게 보내는 그 여자의 답가\n애절한 이별 후에도, 설레는 사랑의 시작에도\n라푸마가 함께합니다.|

### Entity-Relationship Diagram

![Entity-Relationship Diagram](https://user-images.githubusercontent.com/92344242/151416449-a431a8da-0aab-4927-9bab-256554220072.png)

- Video: 영상 고유의 정보들로 구성
  - 영상 ID(Video_id)
  - 영상 제목(Title)
  - 채널 이름(Channel_title)

- Information: 고유 정보를 제외한 영상의 정보들로 구성
  - 조회수(Views)
  - 좋아요 수(Likes)
  - 싫어요 수(Dislikes)
  - 태그(tag)

- Date: 영상의 날짜 및 시간 정보로 구성
  - 트렌드에 오른 날짜(Trending_date)
  - 게시일(Publish_time)

- Category: 유튜브의 카테고리 정보로 구성
  - 카테고리 번호(Category_id)
  - 카테고리명(Category_title)

### 실제 테이블

![실제 테이블 이미지](https://user-images.githubusercontent.com/92344242/151416595-160839ce-aea5-42b4-9d44-e990b464be7e.png)

- 특이사항
  - Video는 Category 테이블의 category_id를 참조한다.
  - Information, Info_tag, Date는 Video 테이블의 video_id를 참조한다.
  - 영상 정보 중 태그 정보에 대해서는 Info_tag라는 테이블로 따로 분리하였다.

## 기술 스택
- Back-End: Python
- Front-End: HTML/CSS, Bootstrap
- Database: SQLite

## 주요 기능
- 카테고리별로 인기 태그 상위 10개 조회하기
- 입력한 태그에 대하여 카테고리별로 등장 빈도 조회하기
- 입력한 태그를 포함하는 영상 조회하기
- 카테고리별로 영상 조회하기
- 태그, 조회수, 좋아요 수, 싫어요 수를 이용하여 카테고리 예측해보기
  - 학습 목적으로 강의에서 제공된 Decision Tree 예제 코드를 재구성하였다. (@author kong_)
    - Feature 추출 과정 (extract_features)
      1. 카테고리별로 태그 정보를 저장한다. 태그 정보에는 태그 명과 등장 빈도수 정보가 담겨있다.
      2. 카테고리별로 태그 정보 중 등장 빈도수에 대한 중간값을 찾는다.
      3. 중간값 이상 등장하는 태그를 리스트에 저장한다.
      
    - 학습 데이터 구성 (make_feature)
      1. Feature 추출 과정을 통해 추출된 태그 정보를 포함하는지를 저장한다.
      2. 조회수, 좋아요 수, 싫어요 수를 저장한다.
    
    - Decision Tree 구성 (make_dec_tree)
      1. 구성된 학습 데이터를 이를 이용하여 카테고리 번호를 예측하도록 학습시킨다.

---

## 참고 이미지
### 카테고리별로 인기 태그 상위 10개 조회하기

![카테고리별 인기 태그 상위 10개 조회](https://user-images.githubusercontent.com/92344242/151417639-63efa525-282a-4da6-8389-bc1e17417037.jpeg)

### 입력한 태그에 대하여 카테고리별로 등장 빈도 조회하기

![카테고리별 태그 등장빈도 조회](https://user-images.githubusercontent.com/92344242/151417684-eadbd547-db57-4231-8a5a-d3b604d67811.jpeg)

### 입력한 태그를 포함하는 영상 조회하기

![태그를 통한 영상 검색 기능](https://user-images.githubusercontent.com/92344242/151417704-bab195ae-0a33-48b5-b80e-f876e7b6e22b.jpeg)


### 카테고리별로 영상 조회하기

![카테고리별 영상 조회 기능](https://user-images.githubusercontent.com/92344242/151417777-ca7e835c-b6d6-4707-b155-ee9003c68efa.jpeg)

### 태그, 조회 수, 좋아요 수, 싫어요 수를 이용하여 카테고리 예측해보기

![태그, 조회수, 좋아요 수, 싫어요 수를 이용하여 카테고리 예측해보기](https://user-images.githubusercontent.com/92344242/151417794-68948d6c-be81-477c-936b-64516c8c9509.jpeg)

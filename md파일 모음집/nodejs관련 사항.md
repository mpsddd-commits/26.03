
# node.js는 단독으로 백엔드에서 사용할 수 있게 만든 프로그램. 홈페이지 첫 장면은 백엔드 시작할때 구동하는(?) 코드 이다.
# ES와 CJS코드방식 헷갈리지 말기!
# npm init -y -> dir -> index.js파일 설치 -> npm run test 
# 실행 할때 node index.js (XXXXXX!!XXXX) -> npm run으로 기입해야함
# npm으로는 start라는 고정값이 아닌 자유로운 key로 선언해도 된다.
# node_modules가 설치 되었다  -> 이 파일 프로젝트당 패키지가 설치 되었다. ==> 각 파일마다 프로젝트 모듈을 설치 해야한다! = npm i nodemon ===> 
# nodemon 모듈즈 파일이 크기 때문에 제외한 3개의 파일(패키지.패키지락.인덱스js)만 가져가며 다른 컴퓨터에서 사용할때 모듈즈 제외한 파일들만 모으고 "npm i"만 설치하면 package.json 내부 dependencies에 있는 버젼으로 자동 설치 된다.

# npm run dev하면 노드몬 자동 설치가 되고 실시간 기록이 된다. 오토세이브 된 상태에서 진행하면 자꾸 기록되고 오류가 날 수 있으니 오토 세이브 끌 수 있게 하자.

# 보통 index.js에 짧게 기입하고 다른 js파일 생성 후 그걸 import, export를 통해 for문 등 긴것을 사용한다. 
# 기본 설정 패키지js파일에서 nodejs메인사이트잇는거 인덱스 파일에 복붙 후 패키지 js파일 타입에 commonjs에서 module로 바꾸면 es버젼으로 바뀐다.
# dev가 생성되면 웹사이트에서 오는 요청을 기다리고있다. = Listening on 127.0.0.1:3000
# 'Content-Type': 'text/html; charset=utf-8'이라고 writehead쪽에 기입하면 값이 나온다. (이쪽이 vs코드에 head에 해당하는 부분이라 생각하면 된다.)
# 임포트할때 다른 js파일에서 함수표현을 선언하고 불러오기 할때 ()는 없어진다. 
# http 기술  => 저 주소로 요청을 보낼 수 있게 준비하는 기술 (요청 대기상태) => 웹개발 기술.
# cd.. -지우기1
# rmdir /s /q .test -지우기2

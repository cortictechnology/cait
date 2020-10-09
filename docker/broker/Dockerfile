FROM erlang
RUN git clone https://github.com/emqx/emqx-rel.git 
WORKDIR emqx-rel
RUN make

FROM erlang:slim
WORKDIR /root/
COPY --from=0 /emqx-rel/_build/emqx/rel .

COPY start_broker.sh /
